# -*- UTF-8 -*-
# ui/banner.py

import os
import time

from colorama import Fore, init
init(autoreset=True)

from core.stats import Stats, _stats_lock
from core.config import (
    __version__,
    Config,
    Globals
)

from utils.utility import utility as utils
from ui.table import Table, Theme



class Banners:
    @staticmethod
    def MainBanner(margin_left: int = 2) -> str:
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
    def MiniBanner(margin_left: int = 2) -> str:
        margin_left = margin_left if margin_left is not None else 0
        margin_left_space = ' ' * margin_left
        return f'''
{(margin_left_space)}░█▀▀░█░█░█▀▀░█▀▀░█░█░█░█░█▀▄░█▀█░█▀▀░█░█░█▀▀░█▀▄
{(margin_left_space)}░█░░░█▀█░▀▀█░▀▀█░█▀█░█▀▄░█▀▄░█▀█░█░░░█▀▄░█▀▀░█▀▄
{(margin_left_space)}░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░▀░▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀
    '''


class BannerStats:
    def __init__(self, total_tasks: int):
        self.total_tasks = total_tasks
        self.theme = Theme(Fore.WHITE, Fore.CYAN)
        self.targets = os.path.basename(Config.IP_FILE)
        self.version = __version__
        self.timeout = Config.TIMEOUT
        self.max_worker = Config.MAX_WORKERS
        self.per_worker = Config.CONCURRENT_PER_WORKER

    def run(self):
        while True:
            table = Table(self.theme, parent_padding=4)
            with _stats_lock:
                goods = Stats.Goods.get()
                errors = Stats.Errors.get()
                honeypots = Stats.Honeypots.get()
            total_connections = goods + errors + honeypots
            elapsed = max(0.001, time.perf_counter() - Globals._start_time_monotonic)
            cps = total_connections / elapsed
            remaining = max(0.0, (self.total_tasks - total_connections) /
                cps) if cps > 0 else 0.0
            success_total = goods + honeypots

            utils.clear_screen()

            table.add_block([f'Advanced Ch4120N SSH Brute Force Tool v{self.version}'])
            table.add_block([f'File: {self.targets} | Timeout: {self.timeout}s',
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
                            f"Enhanced Multi-Layer Workers v{self.version}"])

            print(table.display())

            if total_connections == self.total_tasks:
                Globals._stop_event.set()
                break