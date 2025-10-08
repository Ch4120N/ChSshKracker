# -*- UTF-8 -*-
# ui/banner.py

import os
import time

from colorama import Fore, init

from core.config import (
    BRUTE_FORCE_STOP_EVENT, 
    globalConfig,
    FILES_PATH,
    STATS,
    __version__
)

from utils.utils import utils
from ui.table import Table, Theme

init(autoreset=True)


class Banners:
    @staticmethod
    def MainBanner(margin_left:int = None) -> str:
        margin_left = margin_left if margin_left is not None else 0
        margin_left_space = ' ' * margin_left
        return f'''
{(margin_left_space)} ██████╗██╗  ██╗███████╗███████╗██╗  ██╗██╗  ██╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
{(margin_left_space)}██╔════╝██║  ██║██╔════╝██╔════╝██║  ██║██║ ██╔╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
{(margin_left_space)}██║     ███████║███████╗███████╗███████║█████╔╝ ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
{(margin_left_space)}██║     ██╔══██║╚════██║╚════██║██╔══██║██╔═██╗ ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
{(margin_left_space)}╚██████╗██║  ██║███████║███████║██║  ██║██║  ██╗██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
{(margin_left_space)} ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
    '''

    @staticmethod
    def MiniBanner(margin_left:int = None) -> str:
        margin_left = margin_left if margin_left is not None else 0
        margin_left_space = ' ' * margin_left
        return f'''
{(margin_left_space)}░█▀▀░█░█░█▀▀░█▀▀░█░█░█░█░█▀▄░█▀█░█▀▀░█░█░█▀▀░█▀▄
{(margin_left_space)}░█░░░█▀█░▀▀█░▀▀█░█▀█░█▀▄░█▀▄░█▀█░█░░░█▀▄░█▀▀░█▀▄
{(margin_left_space)}░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀
    '''

class BannerStat:
    def __init__(self, total_tasks: int):
        self.total_tasks = total_tasks
        self.theme = Theme(Fore.WHITE, Fore.CYAN)
        self.targets = os.path.basename(FILES_PATH.IP_FILE)
        self.timeout = globalConfig.TIMEOUT_SECS
        self.max_worker = globalConfig.MAX_WORKERS
        self.per_worker = globalConfig.CONCURRENT_PER_WORKER

    def run(self):
        while not BRUTE_FORCE_STOP_EVENT.is_set():
            table = Table(self.theme, parent_border=4)
            with STATS.STATS_LOCK:
                goods = STATS.GOODS
                errors = STATS.ERRORS
                honeypots = STATS.HONEYPOTS
            total_connections = goods + errors + honeypots
            elapsed = max(0.001, time.perf_counter() - globalConfig.START_TIME_MONOTONIC)
            cps = total_connections / elapsed
            remaining = max(0.0, (self.total_tasks - total_connections) /
                cps) if cps > 0 else 0.0
            success_total = goods + honeypots

            utils.clear_screen()
            
            table.add_block([f'Advanced Ch4120N SSH Brute Force Tool v{__version__}'])
            table.add_block([f'File: {self.files} | Timeout: {self.timeout}s',
                            f'Max Workers: {self.max_worker} | Per Worker: {self.per_worker}']
                            )
            table.add_block([f'Checked SSH: {total_connections}/{self.total_tasks}',
                            f'Speed: {cps:.2f} checks/sec',
                            *([f'Elapsed: {utils.format_duration(elapsed)}',
                                f'Remaining: {utils.format_duration(remaining)}'
                                ] if total_connections < self.total_tasks else 
                                [f'Total Time: {utils.format_duration(elapsed)}',
                                f'Scan Completed Successfully!'
                                ]
                            )])
            table.add_block([
                f'Successful: {goods}',
                f'Failed: {errors}',
                f'Honeypots: {honeypots}',
                *(
                    [
                        f"Success Rate: {100.0 * goods / (success_total):.2f}%",
                        f"Honeypot Rate: {100.0 * honeypots / (success_total):.2f}%"
                    ]
                    if total_connections > 0 and (success_total) > 0 else []
                )
            ])
            table.add_block(['Powered By Ch4120N',
                            f"Enhanced Multi-Layer Workers v{__version__}",
                            "Licence CGBL (Charon General Black Licence)"])

            print(table.display())
            