# -*- UTF-8 -*-
# ChSshKracker.py

import os
import sys
import signal
try:
    import paramiko
    from colorama import Fore, init
    from prompt_toolkit import prompt
    init(autoreset=True)
except ImportError:
    sys.exit('\n [ - ] Please install requirements libraries. Using commands below:\n' \
             '\t- python -m pip install cryptography==40.0.2 paramiko==3.4.0 colorama==0.4.6 prompt_toolkit==3.0.52\n' \
             '\t- Or\n' \
             '\t- python -m pip install -r requirements.txt\n'
            )

from core.config import (
    globalConfig,
    FILES_PATH,
    SUMMARY
)
from utils.io_utils import IO
from ui.decorators import MsgDCR
from ui.summary_render import SummaryRenderer
from cli.interactive import InteractiveUI
from cli.parser import Parser
from cli.signals import handle_SIGINT


class ChSSHKracker:
    def __init__(self):
        signal.signal(signal.SIGINT, handle_SIGINT)
        self.summary = SUMMARY
        self.parser_obj = Parser()
    
    def run(self):
        self.parser_obj.build_parser()
        

if __name__ == '__main__':
    ChSSHKracker()