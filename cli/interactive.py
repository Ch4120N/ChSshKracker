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
    Config
)

from ui.banner import Banners
from ui.decorators import MsgDCR
from ui.summary_render import SummaryRenderer, GetSummary
from cli.path_completer import PathCompleter


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
            'bluebrackets' : 'blue bold',
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
    