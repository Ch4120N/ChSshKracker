# -*- UTF-8 -*-
# cli/parser.py

import argparse
from typing import Callable

from core.config import (
    __version__,
    SCRIPT_NAME,
    SCRIPT_DESCRIPTION,
    globalConfig
)
from ui.sharp_box import SharpBox