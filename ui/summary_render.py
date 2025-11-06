# -*- UTF-8 -*-
# ui/summary_render.py

import shutil
import sys
from typing import Optional, List

from colorama import Fore, init
init(autoreset=True)

from core.config import Config, FILE_PATH
from ui.decorators import MsgDCR

class SummaryRenderer:
    def __init__(self, title: str = 'Configuration Summary', space: int = 5, global_margin_left_spaces: int = 2, text_margin_left: int = 2, max_width: int = 80) -> None:
        self.title = title
        self.space = space
        self.global_margin_left = ' ' * global_margin_left_spaces
        self.text_margin_left = ' ' * text_margin_left
        self.max_pref_width = max_width

    def render(self, summary: dict) -> None:
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        max_line_width = min(terminal_width, self.max_pref_width)
        spaces = ' ' * self.space
        max_key_length = max((len(str(k))
                             for k in summary if summary[k]), default=0)

        
        padding = (max_line_width - len(self.title) - 4) // 2
        padding = max(padding, 5)
        print(self.global_margin_left + '═' * padding + f' {self.title} ' + '═' * padding)

        for key, value in summary.items():
            if value is None or value == '' or value == 0:
                continue
            key_str = str(key)
            value_str = str(value)
            line = f"{self.global_margin_left}{self.text_margin_left}{key_str:<{max_key_length}}{spaces}: {value_str}"
            if len(line) > max_line_width:
                wrap_width = max_line_width - max_key_length - len(spaces) - 6
                wrapped_value = [value_str[i:i+wrap_width]
                                 for i in range(0, len(value_str), wrap_width)]
                print(
                    f"{self.global_margin_left}{self.text_margin_left}{key_str:<{max_key_length}}{spaces}: {wrapped_value[0]}")
                for part in wrapped_value[1:]:
                    print(
                        f"{Fore.LIGHTWHITE_EX}{self.global_margin_left}{self.text_margin_left}{' ' * (max_key_length + len(spaces) + 2)}{part}")
            else:
                print(line)

        print(self.global_margin_left + '═' * (max_line_width - 3))

class GetSummary:
    def __init__(self):
        self.summary = {}

    def add_if_exists(self, kv: List[str]):
        if len(kv) > 2 or len(kv) < 2:
            MsgDCR.FailureMessage('Invalid parameter for summaryes')
            sys.exit(2)

        key = kv[0]
        value = kv[1]

        if value is not None and str(value).strip() != '':
            self.summary[key] = value
    
    def get(self, summary: Optional[dict[str, str]] = None):
        if (summary is not None or summary):
            self.summary = summary
        
        return self.summary

    def get_ips(self):
        if Config.IP_FILE:
            return ['IP LIST', f"{Fore.LIGHTWHITE_EX}{Config.IP_FILE}"]
        else:
            return ['IP LIST', '']
    
    def confirm_use_combo(self):
        if Config.USE_COMBO:
            return ['USE COMBO LIST', f'{Fore.LIGHTCYAN_EX}YES']
        else:
            return ['USE COMBO LIST', f'{Fore.LIGHTCYAN_EX}NO']
    
    def get_combo_file(self):
        if Config.USE_COMBO:
            return ['COMBO LIST', f"{Fore.LIGHTWHITE_EX}{Config.COMBO_FILE}"]
        else:
            return ['COMBO LIST', f"{Fore.LIGHTWHITE_EX}{FILE_PATH.COMBO_FILE}"]
    
    def get_user_file(self):
        if Config.USERNAME_FILE:
            return ['USERNAME LIST', f'{Fore.LIGHTWHITE_EX}{Config.USERNAME_FILE}']
        else:
            return ['USERNAME LIST', '']
    
    def get_pass_file(self):
        if Config.PASSWORD_FILE:
            return ['PASSWORD LIST', f'{Fore.LIGHTWHITE_EX}{Config.PASSWORD_FILE}']
        else:
            return ['PASSWORD LIST', '']
    
    def get_timeout(self):
        timeout = ''
        if (Config.TIMEOUT < 10):
            timeout = f'0{Config.TIMEOUT}'
        else:
            timeout = str(Config.TIMEOUT)
        if (Config.TIMEOUT == 5):
            timeout = f'{timeout} {Fore.LIGHTBLUE_EX}({Fore.LIGHTRED_EX}DEFAULT{Fore.LIGHTBLUE_EX}){Fore.RESET}'
        
        return Fore.LIGHTWHITE_EX + timeout
    
    def get_max_workers(self):
        max_workers = ''
        if (Config.MAX_WORKERS < 10):
            max_workers = f'0{Config.MAX_WORKERS}'
        else:
            max_workers = str(Config.MAX_WORKERS)
        
        if (Config.MAX_WORKERS == 25):
            max_workers = f'{max_workers} {Fore.LIGHTBLUE_EX}({Fore.LIGHTRED_EX}DEFAULT{Fore.LIGHTBLUE_EX}){Fore.RESET}'
        
        return Fore.LIGHTWHITE_EX + max_workers

    def get_per_worker(self):
        per_worker = ''
        if (Config.CONCURRENT_PER_WORKER < 10):
            per_worker = f'0{Config.CONCURRENT_PER_WORKER}'
        else:
            per_worker = str(Config.CONCURRENT_PER_WORKER)
        
        if (Config.CONCURRENT_PER_WORKER == 25):
            per_worker = f'{per_worker} {Fore.LIGHTBLUE_EX}({Fore.LIGHTRED_EX}DEFAULT{Fore.LIGHTBLUE_EX}){Fore.RESET}'
        
        return Fore.LIGHTWHITE_EX + per_worker