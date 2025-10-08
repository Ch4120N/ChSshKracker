# -*- UTF-8 -*-
# cli/interactive.py

import os
import signal
from threading import Event
from types import FrameType
from typing import Optional

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts.prompt import CompleteStyle
from colorama import Fore, init
init(autoreset=True)

from core.config import (
    globalConfig,
    FILES_PATH,
    DEFAULT_PATH,
    SUMMARY
)

from ui.banner import Banners
from ui.decorators import MsgDCR
from ui.summary_render import SummaryRenderer
from utils.utils import utils
from cli.path_completer import PathCompleter
from cli.signals import handle_SIGINT

class Inputs:
    def __init__(self):
        self.INPUT_DECORATOR = [
            ('class:brackets', '\n [ '),
            ('class:arrow', '>'),
            ('class:brackets', ' ] ')
        ]
    def build_input_styles(self, prompt_color: str = 'white bold') -> Style:
        return Style.from_dict({
            'prompt': 'ansired bold',
            'brackets': 'blue bold',
            'arrow': 'magenta bold',
            'text': prompt_color,
            'key': 'red bold',
            'confirmcolor': 'cyan bold'
        })

    def input_with_prompt(self, prompt_message, completer_on: bool = False, prompt_color: str = 'white bold') -> str:
        try:
            return prompt(prompt_message,
                        completer=PathCompleter() if completer_on else None,
                        # complete_style=CompleteStyle.READLINE_LIKE, # Optional
                        style=self.build_input_styles(prompt_color)
                        ).strip()
        except (KeyboardInterrupt, EOFError):
            handle_SIGINT(1, None)
        except RuntimeError:
            return ''

    def input_continue(self) -> None:
        prompt_message = [
            self.INPUT_DECORATOR,
            ('class:text', 'Press '),
            ('class:brackets', '['),
            ('class:key', 'ENTER'),
            ('class:brackets', ']'),
            ('class:text', ' key to continue /Or Press '),
            ('class:brackets', '['),
            ('class:key', 'CTRL+C'),
            ('class:brackets', ']'),
            ('class:text', ' hotkey to exit ...'),
        ]
        self.input_with_prompt(prompt_message)

    def input_start_attack(self) -> None:
        prompt_message = [
            self.INPUT_DECORATOR,
            ('class:text', 'Press '),
            ('class:brackets', '['),
            ('class:key', 'ENTER'),
            ('class:brackets', ']'),
            ('class:text', ' key to start brute forcing /Or Press '),
            ('class:brackets', '['),
            ('class:key', 'CTRL+C'),
            ('class:brackets', ']'),
            ('class:text', ' hotkey to exit ...'),
        ]
        self.input_with_prompt(prompt_message)

    # Interactive Inputs

    def input_get_ip_file(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Enter the path to the IP list file: ')
            ], completer_on=True)
    
    def input_continue_with_combos(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Do you want to provide a combo file instead of separate user/password lists?'),
            ('class:brackets', ' ( '),
            ('class:confirmcolor', 'y/n'),
            ('class:brackets', ' ) '),
            ('class:text', ': ')
            ]).lower()
    
    def input_get_combo_file(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Enter the path to the generated combo file: ')
            ], completer_on=True)
    
    def input_get_user_file(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Enter the path to the username list file: ')
            ], completer_on=True)

    def input_get_password_file(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Enter the path to the password list file: ')
            ], completer_on=True)

    def input_get_timeout(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Enter the connection timeout in seconds'),
            ('class:brackets', ' ('),
            ('class:confirmcolor', f'Default: {globalConfig.TIMEOUT_SECS}'),
            ('class:brackets', ') '),
            ('class:text', ': ')
            ])
    
    def input_get_max_workers(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Enter the maximum number of workers'),
            ('class:brackets', ' ('),
            ('class:confirmcolor', f'Default: {globalConfig.MAX_WORKERS}'),
            ('class:brackets', ') '),
            ('class:text', ': ')
            ])
    
    def input_get_per_workers(self):
        return self.input_with_prompt([
            ('class:brackets', '\n [ '),
            ('class:arrow', '>'),
            ('class:brackets', ' ] '),
            ('class:text', 'Enter the number of concurrent connections per worker'),
            ('class:brackets', ' ('),
            ('class:confirmcolor',
                f'Default: {globalConfig.CONCURRENT_PER_WORKER}. '),
            ('class:key', 'Recommended'),
            ('class:brackets', ') '),
            ('class:text', ': ')
            ])
    
    def input_confirm_configurations(self):
        return self.input_with_prompt([
            self.INPUT_DECORATOR,
            ('class:text', 'Do you want to change any other settings?'),
            ('class:brackets', ' ( '),
            ('class:confirmcolor', 'y/n'),
            ('class:brackets', ' ) '),
            ('class:text', ': ')
            ]).lower()



class InteractiveUI:
    def __init__(self):
        self.summary = SUMMARY
        self.summary_obj = SummaryRenderer(
            title='Configuration Summary', 
            space=5, 
            margin_left_spaces=2, 
            max_width=80
        )
        self.inputs = Inputs()

        # Requirements Events
        self.MAIN_EVENT = Event()
        self.REQUIRED_IP_EVENT = Event()
        self.USE_COMBO_CONFIRMATION = Event()
        self.REQUIRED_COMBO_FILE_EVENT = Event()
        self.REQUIRED_USER_FILE_EVENT = Event()
        self.REQUIRED_PASS_FILE_EVENT = Event()
        self.REQUIRED_TIMEOUT_EVENT = Event()
        self.REQUIRED_MAX_WORKERS_EVENT = Event()
        self.REQUIRED_PER_WORKERS_EVENT = Event()

    def _print_banner(self):
        print(Fore.LIGHTRED_EX + Banners.MainBanner(margin_left=2) + Fore.RESET, '\n')
    
    def _continue(self):
        self.inputs.input_continue()
    
    def run(self):
        while not self.MAIN_EVENT.is_set():
            self.get_ips()
            self.get_combos_or_userpass()
            self.get_timeout()
            self.get_max_workers()
            self.get_per_workers()
        
    def get_ips(self):
        while not self.REQUIRED_IP_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()

            ip_list = self.inputs.input_get_ip_file()
            ip_path = os.path.realpath(ip_list)

            if (not ip_list):
                MsgDCR.FailureMessage("IP list is required!")
                self._continue()
                continue
        
            elif (
                (not os.path.isfile(ip_path)) 
                or 
                (not os.path.exists(ip_path))
                ):
                MsgDCR.FailureMessage(f'IP list does not exist: {ip_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_IP_EVENT.set()
        
        self.summary['IP FILE'] = ip_path
        FILES_PATH.IP_FILE = ip_path
        
    
    def get_combos_or_userpass(self):
        while not self.USE_COMBO_CONFIRMATION.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.summary)

            use_combo = self.inputs.input_continue_with_combos()

            if (not use_combo) or (not use_combo in ['y', 'n']):
                MsgDCR.FailureMessage('Please enter valid input: y/n ')
                self._continue()
                continue
        
            elif (use_combo in ['y']):
                self.summary['USE COMBO'] = 'YES'
                self.get_combo_file()
                self.USE_COMBO_CONFIRMATION.set()
            
            elif (use_combo in ['n']):
                self.summary['USE COMBO'] = 'NO'
                self.summary['COMBO FILE'] = DEFAULT_PATH.COMBO_FILE
                self.get_user_file()
                self.get_pass_file()
                self.USE_COMBO_CONFIRMATION.set()
            else:
                MsgDCR.FailureMessage('Something went wrong. Please try again!')
                self._continue()
                continue

    def get_combo_file(self):
        while not self.REQUIRED_COMBO_FILE_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.summary)

            combo_list = self.inputs.input_get_combo_file()
            combo_path = os.path.realpath(combo_list)

            if (not combo_list):
                MsgDCR.FailureMessage('Combo list path is required if you choosing to use a combo list')
                self._continue()
                continue

            elif (
                (not os.path.isfile(combo_path)) 
                or 
                (not os.path.exists(combo_path))
                ):
                MsgDCR.FailureMessage(f'Combo list does not exist: {combo_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_COMBO_FILE_EVENT.set()

        self.summary['COMBO FILE'] = combo_path
        self.summary['USERNAME FILE'] = 'N/A'
        self.summary['PASSWORD FILE'] = 'N/A'
        FILES_PATH.COMBO_FILE = combo_path
    
    def get_user_file(self):
        while not self.REQUIRED_USER_FILE_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.summary)

            user_list = self.inputs.input_get_user_file()
            user_path = os.path.realpath(user_list)

            if (not user_list):
                MsgDCR.FailureMessage('Username list is required if your not using a combo list')
                self._continue()
                continue

            elif (
                (not os.path.isfile(user_path)) 
                or 
                (not os.path.exists(user_path))
                ):
                MsgDCR.FailureMessage(f'Username list does not exist: {user_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_USER_FILE_EVENT.set()

        self.summary['USERNAME FILE'] = user_path
        FILES_PATH.USERNAME_FILE = user_path

    def get_pass_file(self):
        while not self.REQUIRED_PASS_FILE_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.summary)

            pass_list = self.inputs.input_get_password_file()
            pass_path = os.path.realpath(pass_list)

            if (not pass_list):
                MsgDCR.FailureMessage('Password list is required if your not using a combo list')
                self._continue()
                continue

            elif (
                (not os.path.isfile(pass_path)) 
                or 
                (not os.path.exists(pass_path))
                ):
                MsgDCR.FailureMessage(f'Password list does not exist: {pass_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_PASS_FILE_EVENT.set()

        self.summary['PASSWORD FILE'] = pass_path
        FILES_PATH.PASSWORD_FILE = pass_path

    def get_timeout(self):
        while not self.REQUIRED_TIMEOUT_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.summary)

            timeout = self.inputs.input_get_timeout()

            if (not timeout):
                self.REQUIRED_TIMEOUT_EVENT.set()
            elif (
                (not timeout.isdigit()) 
                or 
                (int(timeout) < 1)
                ):
                MsgDCR.FailureMessage('Please enter valid positive integer for timeout')
                self._continue()
                continue
            else:
                self.REQUIRED_TIMEOUT_EVENT.set()

        self.summary['TIMEOUT (S)'] = timeout
        globalConfig.TIMEOUT_SECS = int(timeout)
    
    def get_max_workers(self):
        while not self.REQUIRED_MAX_WORKERS_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.summary)

            max_workers = self.inputs.input_get_max_workers()

            if (not max_workers):
                self.REQUIRED_MAX_WORKERS_EVENT.set()
            elif (
                (not max_workers.isdigit()) 
                or 
                (int(max_workers) < 1)
                ):
                MsgDCR.FailureMessage('Please enter valid positive integer for max workers')
                self._continue()
                continue
            else:
                self.REQUIRED_MAX_WORKERS_EVENT.set()

        self.summary['MAX WORKERS'] = max_workers
        globalConfig.MAX_WORKERS = int(max_workers)
    
    def get_per_workers(self):
        while not self.REQUIRED_PER_WORKERS_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.summary)

            per_worker = self.inputs.input_get_per_workers()

            if (not per_worker):
                self.REQUIRED_PER_WORKERS_EVENT.set()
            elif (
                (not per_worker.isdigit()) 
                or 
                (int(per_worker) < 1)
                ):
                MsgDCR.FailureMessage('Please enter valid positive integer for per worker')
                self._continue()
                continue
            else:
                self.REQUIRED_PER_WORKERS_EVENT.set()

        self.summary['PER WORKER'] = per_worker
        globalConfig.CONCURRENT_PER_WORKER = int(per_worker)