# -*- UTF-8 -*-
# cli/interactive.py

import os
import signal
import threading
from pathlib import Path
from types import FrameType
from typing import Optional

from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts.prompt import CompleteStyle

from core.config import (
    globalConfig,
    FILES_PATH,
    SUMMARY
)

from ui.banner import Banners
from ui.decorators import MsgDCR
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

    def input_ip_list(self):
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



