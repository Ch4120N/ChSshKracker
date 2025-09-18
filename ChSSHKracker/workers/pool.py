from __future__ import annotations

import concurrent.futures as futures
import threading
import time
import gc
import signal
import sys
from collections import defaultdict
from datetime import timedelta
from typing import Dict, Iterable, List, Set, Tuple, Optional
import psutil

from ..config import CONCURRENT_PER_WORKER, get_optimal_worker_count, get_optimal_concurrent_per_worker
from ..models import HoneypotDetector, SSHTask, ServerInfo
from ..ssh.client import SSHClient
from ..ssh.system_info import gather_system_info
from ..detection.honeypot import detect_honeypot
from ..utils.logging_utils import log_success, log_honeypot


class ResourceMonitor:
    """Monitor system resources and adjust worker behavior"""
    def __init__(self, max_memory_mb: int = 512, max_cpu_percent: float = 80.0):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.process = psutil.Process()
        self._lock = threading.Lock()
        self._should_throttle = False
        
    def check_resources(self) -> bool:
        """Check if system resources are within limits"""
        try:
            memory_mb = self.process.memory_info().rss / (1024 * 1024)
            cpu_percent = self.process.cpu_percent()
            
            with self._lock:
                self._should_throttle = (
                    memory_mb > self.max_memory_mb or 
                    cpu_percent > self.max_cpu_percent
                )
                return not self._should_throttle
        except Exception:
            return True  # If we can't check, assume OK
    
    def should_throttle(self) -> bool:
        with self._lock:
            return self._should_throttle


class Stats:
    def __init__(self) -> None:
        self.goods = 0
        self.errors = 0
        self.honeypots = 0
        self._lock = threading.Lock()

    def add_good(self) -> None:
        with self._lock:
            self.goods += 1

    def add_error(self) -> None:
        with self._lock:
            self.errors += 1

    def add_honeypot(self) -> None:
        with self._lock:
            self.honeypots += 1


def calculate_task_buffer(max_workers: int) -> int:
    return min(max_workers * 10, 1000)  # Much smaller buffer to save memory


def process_task(task: SSHTask, timeout_seconds: int, stats: Stats, seen: Set[Tuple[str, str]], 
                resource_monitor: ResourceMonitor, concurrent_limit: int) -> None:
    # Check resources before processing
    if resource_monitor.should_throttle():
        time.sleep(0.1)  # Brief pause to reduce load
        return
        
    key = (task.ip, task.port)
    # prevent duplicate success processing similar to Go map
    if key in seen:
        return
        
    client = SSHClient(task.ip, int(task.port), task.username, task.password, timeout_seconds)
    started = time.perf_counter()
    try:
        client.connect()
    except Exception:
        stats.add_error()
        return

    server = ServerInfo(
        ip=task.ip,
        port=task.port,
        username=task.username,
        password=task.password,
        response_time=timedelta(seconds=(time.perf_counter() - started)),
    )
    try:
        gather_system_info(client, server)
        detector = HoneypotDetector(time_analysis=True, command_analysis=True, network_analysis=True)
        server.is_honeypot = detect_honeypot(client, server, detector)
        if not server.is_honeypot:
            seen.add(key)
            stats.add_good()
            log_success(server)
        else:
            stats.add_honeypot()
            log_honeypot(server)
    finally:
        client.close()
        # Force garbage collection to free memory
        if stats.goods % 100 == 0:  # Every 100 successful connections
            gc.collect()


def run_pool(tasks: Iterable[SSHTask], max_workers: int, timeout_seconds: int, stats: Stats, 
            max_memory_mb: int = 512, max_cpu_percent: float = 80.0) -> None:
    """Optimized worker pool with resource monitoring and adaptive limits"""
    
    # Auto-adjust workers based on system resources
    optimal_workers = get_optimal_worker_count()
    optimal_concurrent = get_optimal_concurrent_per_worker()
    
    # Use the more conservative setting
    actual_workers = min(max_workers, optimal_workers)
    actual_concurrent = min(CONCURRENT_PER_WORKER, optimal_concurrent)
    
    print(f"Using {actual_workers} workers with {actual_concurrent} concurrent connections each")
    
    # Resource monitoring
    resource_monitor = ResourceMonitor(max_memory_mb, max_cpu_percent)
    seen: Set[Tuple[str, str]] = set()
    lock = threading.Lock()
    
    # Process tasks in smaller batches to reduce memory usage
    batch_size = min(100, actual_workers * actual_concurrent)
    tasks_list = list(tasks)
    
    def process_batch(batch: List[SSHTask]) -> None:
        """Process a batch of tasks with resource monitoring"""
        sem = threading.Semaphore(actual_concurrent)
        threads = []
        
        for task in batch:
            if resource_monitor.should_throttle():
                time.sleep(0.05)  # Throttle when resources are high
                
            sem.acquire()
            thread = threading.Thread(
                target=lambda t=task: (process_task_wrapper(t), sem.release()),
                daemon=True,
            )
            thread.start()
            threads.append(thread)
            
        # Wait for all threads in this batch
        for thread in threads:
            thread.join()
            
        # Check resources after each batch
        resource_monitor.check_resources()

    def process_task_wrapper(t: SSHTask) -> None:
        with lock:
            local_seen = set(seen)
        process_task(t, timeout_seconds, stats, local_seen, resource_monitor, actual_concurrent)
        with lock:
            seen.update(local_seen)

    # Process tasks in batches
    for i in range(0, len(tasks_list), batch_size):
        batch = tasks_list[i:i + batch_size]
        process_batch(batch)
        
        # Force garbage collection between batches
        gc.collect()

