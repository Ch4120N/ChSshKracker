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



