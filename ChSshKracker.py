# -*- UTF-8 -*-
# ChSshKracker.py

import os
import sys

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

