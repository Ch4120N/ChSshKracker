# -*- UTF-8 -*-
# cli/interactive.py

from __future__ import annotations

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
    _stop_event,
    Config,
    FILE_PATH
)

from cli.path_completer import PathCompleter
from utils.utility import utility as utils
from ui.summary_render import SummaryRenderer, GetSummary
from ui.decorators import MsgDCR
from ui.banner import Banners


def handle_SIGINT(frm, func):
    print()
    MsgDCR.FailureMessage('Program Interrupted By User!')
    _stop_event.set()
    os.kill(os.getpid(), signal.SIGTERM)


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
            'brackets': 'magenta bold',
            'bluebrackets': 'blue bold',
            'arrow': 'white bold',
            'text': prompt_color,
            'key': 'red bold',
            'confirmcolor': 'cyan bold'
        })

    def input_with_prompt(self, prompt_message, completer_on: bool = False, prompt_color: str = 'white bold'):
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
            ('class:text', 'Press '),
            ('class:bluebrackets', '['),
            ('class:key', 'ENTER'),
            ('class:bluebrackets', ']'),
            ('class:text', ' key to continue /Or Press '),
            ('class:bluebrackets', '['),
            ('class:key', 'CTRL+C'),
            ('class:bluebrackets', ']'),
            ('class:text', ' hotkey to exit ...'),
        ]
        self.input_with_prompt(self.INPUT_DECORATOR + prompt_message)

    def input_start_attack(self) -> None:
        prompt_message = [
            ('class:text', 'Press '),
            ('class:bluebrackets', '['),
            ('class:key', 'ENTER'),
            ('class:bluebrackets', ']'),
            ('class:text', ' key to start brute forcing /Or Press '),
            ('class:bluebrackets', '['),
            ('class:key', 'CTRL+C'),
            ('class:bluebrackets', ']'),
            ('class:text', ' hotkey to exit ...'),
        ]
        self.input_with_prompt(prompt_message)

    # Interactive Inputs

    def input_get_ip_file(self):
        prompt_message = [
            ('class:text', 'Enter the path to the IP list file: ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message, completer_on=True)

    def input_continue_with_combos(self):
        prompt_message = [
            ('class:text', 'Do you want to provide a combo file instead of separate user/password lists?'),
            ('class:bluebrackets', ' ( '),
            ('class:confirmcolor', 'y/n'),
            ('class:bluebrackets', ' ) '),
            ('class:text', ': ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message).lower()

    def input_get_combo_file(self):
        prompt_message = [
            ('class:text', 'Enter the path to the generated combo file: ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message, completer_on=True)

    def input_get_user_file(self):
        prompt_message = [
            ('class:text', 'Enter the path to the username list file: ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message, completer_on=True)

    def input_get_password_file(self):
        prompt_message = [
            ('class:text', 'Enter the path to the password list file: ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message, completer_on=True)

    def input_get_timeout(self):
        prompt_message = [
            ('class:text', 'Enter the connection timeout in seconds'),
            ('class:bluebrackets', ' ('),
            ('class:confirmcolor', f'Default: {Config.TIMEOUT}'),
            ('class:bluebrackets', ') '),
            ('class:text', ': ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message)

    def input_get_max_workers(self):
        prompt_message = [
            ('class:text', 'Enter the maximum number of workers'),
            ('class:bluebrackets', ' ('),
            ('class:confirmcolor', f'Default: {Config.MAX_WORKERS}'),
            ('class:bluebrackets', ') '),
            ('class:text', ': ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message)

    def input_get_per_workers(self):
        prompt_message = [
            ('class:text', 'Enter the number of concurrent connections per worker'),
            ('class:bluebrackets', ' ('),
            ('class:confirmcolor',
                f'Default: {Config.CONCURRENT_PER_WORKER}. '),
            ('class:key', 'Recommended'),
            ('class:bluebrackets', ') '),
            ('class:text', ': ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message)

    def input_confirm_configurations(self):
        prompt_message = [
            ('class:text', 'Do you want to change any other settings?'),
            ('class:bluebrackets', ' ( '),
            ('class:confirmcolor', 'y/n'),
            ('class:bluebrackets', ' ) '),
            ('class:text', ': ')
        ]
        return self.input_with_prompt(self.INPUT_DECORATOR + prompt_message).lower()


class InteractiveUI:
    def __init__(self):
        self.summary_obj = SummaryRenderer(
            title='Configuration Summary',
            space=5,
            global_margin_left_spaces=2,
            max_width=80
        )
        self.get_summary_obj = GetSummary()
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
        self.CONFIRM_CONFIGURATION = Event()

    def _clear_events(self):
        self.MAIN_EVENT.clear()
        self.REQUIRED_IP_EVENT.clear()
        self.USE_COMBO_CONFIRMATION.clear()
        self.REQUIRED_COMBO_FILE_EVENT.clear()
        self.REQUIRED_USER_FILE_EVENT.clear()
        self.REQUIRED_PASS_FILE_EVENT.clear()
        self.REQUIRED_TIMEOUT_EVENT.clear()
        self.REQUIRED_MAX_WORKERS_EVENT.clear()
        self.REQUIRED_PER_WORKERS_EVENT.clear()
        self.CONFIRM_CONFIGURATION.clear()

    def _clear_defaults(self):
        Config.TIMEOUT = 5
        Config.MAX_WORKERS = 25
        Config.CONCURRENT_PER_WORKER = 25

    def _clear_file_paths(self):
        Config.IP_FILE = ''
        Config.USERNAME_FILE = ''
        Config.PASSWORD_FILE = ''
        Config.COMBO_FILE = ''

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
            self.get_confirm_configuration()

    def get_ips(self):
        while not self.REQUIRED_IP_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()

            ip_list = self.inputs.input_get_ip_file()
            self.ip_path = os.path.realpath(ip_list) # type: ignore

            if (not ip_list):
                MsgDCR.FailureMessage("IP list is required!")
                self._continue()
                continue

            elif (
                (not os.path.isfile(self.ip_path))
                or
                (not os.path.exists(self.ip_path))
            ):
                MsgDCR.FailureMessage(
                    f'IP list does not exist: {self.ip_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_IP_EVENT.set()

        Config.IP_FILE = self.ip_path
        self.get_summary_obj.add_if_exists(self.get_summary_obj.get_ips())
    
    def get_combos_or_userpass(self):
        while not self.USE_COMBO_CONFIRMATION.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.get_summary_obj.get())

            use_combo = self.inputs.input_continue_with_combos()

            if (not use_combo) or (not use_combo in ['y', 'n']):
                MsgDCR.FailureMessage('Please enter valid input: y/n ')
                self._continue()
                continue
        
            elif (use_combo in ['y', 'yes']):
                Config.USE_COMBO = True
                self.get_summary_obj.add_if_exists(self.get_summary_obj.confirm_use_combo())
                self.get_combo_file()
                self.USE_COMBO_CONFIRMATION.set()
            
            elif (use_combo in ['n', 'no']):
                Config.USE_COMBO = False
                Config.COMBO_FILE = FILE_PATH.COMBO_FILE
                self.get_summary_obj.add_if_exists(self.get_summary_obj.confirm_use_combo())
                self.get_summary_obj.add_if_exists(self.get_summary_obj.get_combo_file())
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
            self.summary_obj.render(self.get_summary_obj.get())

            combo_list = self.inputs.input_get_combo_file()
            self.combo_path = os.path.realpath(combo_list)

            if (not combo_list):
                MsgDCR.FailureMessage('Combo list path is required if you choosing to use a combo list')
                self._continue()
                continue

            elif (
                (not os.path.isfile(self.combo_path)) 
                or 
                (not os.path.exists(self.combo_path))
                ):
                MsgDCR.FailureMessage(f'Combo list does not exist: {self.combo_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_COMBO_FILE_EVENT.set()

        Config.COMBO_FILE = self.combo_path
        self.get_summary_obj.add_if_exists(self.get_summary_obj.get_combo_file())
    
    def get_user_file(self):
        while not self.REQUIRED_USER_FILE_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.get_summary_obj.get())

            user_list = self.inputs.input_get_user_file()
            self.user_path = os.path.realpath(user_list)

            if (not user_list):
                MsgDCR.FailureMessage('Username list is required if your not using a combo list')
                self._continue()
                continue

            elif (
                (not os.path.isfile(self.user_path)) 
                or 
                (not os.path.exists(self.user_path))
                ):
                MsgDCR.FailureMessage(f'Username list does not exist: {self.user_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_USER_FILE_EVENT.set()

        Config.USERNAME_FILE = self.user_path
        self.get_summary_obj.add_if_exists(self.get_summary_obj.get_user_file())

    def get_pass_file(self):
        while not self.REQUIRED_PASS_FILE_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.get_summary_obj.get())

            pass_list = self.inputs.input_get_password_file()
            self.pass_path = os.path.realpath(pass_list)

            if (not pass_list):
                MsgDCR.FailureMessage('Password list is required if your not using a combo list')
                self._continue()
                continue

            elif (
                (not os.path.isfile(self.pass_path)) 
                or 
                (not os.path.exists(self.pass_path))
                ):
                MsgDCR.FailureMessage(f'Password list does not exist: {self.pass_path}')
                self._continue()
                continue
            else:
                self.REQUIRED_PASS_FILE_EVENT.set()

        Config.PASSWORD_FILE = self.pass_path
        self.get_summary_obj.add_if_exists(self.get_summary_obj.get_pass_file())
    
    def get_timeout(self):
        while not self.REQUIRED_TIMEOUT_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.get_summary_obj.get())

            self.timeout_prompt = self.inputs.input_get_timeout()

            if (not self.timeout_prompt):
                self.timeout_prompt = Config.TIMEOUT
                self.REQUIRED_TIMEOUT_EVENT.set()
            elif (
                (not self.timeout_prompt.isdigit()) 
                or 
                (int(self.timeout_prompt) < 1)
                ):
                MsgDCR.FailureMessage('Please enter valid positive integer for timeout')
                self._continue()
                continue
            else:
                self.REQUIRED_TIMEOUT_EVENT.set()

        if (self.timeout_prompt):
            Config.TIMEOUT = int(self.timeout_prompt)
            self.get_summary_obj.add_if_exists(self.get_summary_obj.get_timeout())
    
    def get_max_workers(self):
        while not self.REQUIRED_MAX_WORKERS_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.get_summary_obj.get())

            self.max_workers_prompt = self.inputs.input_get_max_workers()

            if (not self.max_workers_prompt):
                self.max_workers_prompt = Config.MAX_WORKERS
                self.REQUIRED_MAX_WORKERS_EVENT.set()
            elif (
                (not self.max_workers_prompt.isdigit()) 
                or 
                (int(self.max_workers_prompt) < 1)
                ):
                MsgDCR.FailureMessage('Please enter valid positive integer for max workers')
                self._continue()
                continue
            else:
                self.REQUIRED_MAX_WORKERS_EVENT.set()

        if (self.max_workers_prompt):
            Config.MAX_WORKERS = int(self.max_workers_prompt)

    def get_per_workers(self):
        while not self.REQUIRED_PER_WORKERS_EVENT.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.get_summary_obj.get())

            self.per_worker_prompt = self.inputs.input_get_per_workers()

            if (not self.per_worker_prompt):
                self.per_worker_prompt = Config.CONCURRENT_PER_WORKER
                self.REQUIRED_PER_WORKERS_EVENT.set()
            elif (
                (not self.per_worker_prompt.isdigit()) 
                or 
                (int(self.per_worker_prompt) < 1)
                ):
                MsgDCR.FailureMessage('Please enter valid positive integer for per worker')
                self._continue()
                continue
            else:
                self.REQUIRED_PER_WORKERS_EVENT.set()

        if (self.per_worker_prompt):
            Config.CONCURRENT_PER_WORKER = int(self.per_worker_prompt)
    
    def get_confirm_configuration(self):
        self.CONFIRM_CONFIGURATION.clear()
        while not self.CONFIRM_CONFIGURATION.is_set():
            utils.clear_screen()
            self._print_banner()
            self.summary_obj.render(self.get_summary_obj.get())

            confirm = self.inputs.input_confirm_configurations()

            if (not confirm) or (not confirm in ['y', 'yes', 'n', 'no']):
                MsgDCR.FailureMessage('Please enter valid input: y/n ')
                self._continue()
                continue
        
            elif (confirm in ['y', 'yes']):
                self._clear_events()
                self._clear_defaults()
                self._clear_file_paths()
                self.CONFIRM_CONFIGURATION.set()
            
            elif (confirm in ['n', 'no']):
                self.MAIN_EVENT.set()
                self.CONFIRM_CONFIGURATION.set()
            
            else:
                MsgDCR.FailureMessage('Something went wrong. Please try again!')
                self._continue()
                continue