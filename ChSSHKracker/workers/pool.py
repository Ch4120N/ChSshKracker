from __future__ import annotations

import concurrent.futures as futures
import threading
import time
from collections import defaultdict
from datetime import timedelta
from typing import Dict, Iterable, List, Set, Tuple

from ..config import CONCURRENT_PER_WORKER
from ..models import HoneypotDetector, SSHTask, ServerInfo
from ..ssh.client import SSHClient
from ..ssh.system_info import gather_system_info
from ..detection.honeypot import detect_honeypot
from ..utils.logging_utils import log_success, log_honeypot


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
    return int(float(max_workers * CONCURRENT_PER_WORKER) * 1.5)


def process_task(task: SSHTask, timeout_seconds: int, stats: Stats, seen: Set[Tuple[str, str]]) -> None:
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


def run_pool(tasks: Iterable[SSHTask], max_workers: int, timeout_seconds: int, stats: Stats) -> None:
    # per-worker concurrency simulated by chunking tasks into groups handled by each worker thread
    tasks_list = list(tasks)
    seen: Set[Tuple[str, str]] = set()
    lock = threading.Lock()

    def worker_chunk(chunk: List[SSHTask]) -> None:
        sem = threading.Semaphore(CONCURRENT_PER_WORKER)
        thread_group: List[threading.Thread] = []
        for t in chunk:
            sem.acquire()
            th = threading.Thread(
                target=lambda tt=t: (process_task_wrapper(tt), sem.release()),
                daemon=True,
            )
            th.start()
            thread_group.append(th)
        for th in thread_group:
            th.join()

    def process_task_wrapper(t: SSHTask) -> None:
        with lock:
            local_seen = set(seen)
        process_task(t, timeout_seconds, stats, local_seen)
        with lock:
            seen.update(local_seen)

    # Split tasks roughly evenly across workers
    if max_workers <= 0:
        max_workers = 1
    chunks: List[List[SSHTask]] = [
        tasks_list[i::max_workers] for i in range(max_workers)
    ]

    with futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        list(ex.map(worker_chunk, chunks))

