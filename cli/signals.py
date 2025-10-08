# -*- UTF-8 -*-
# cli/signals.py

import os
import signal
from typing import Optional
from types import FrameType

from core.config import BRUTE_FORCE_STOP_EVENT
from ui.decorators import MsgDCR


def handle_SIGINT(frm: int, func: Optional[FrameType]) -> None:
    print()
    MsgDCR.FailureMessage('Program Interrupted By User!')
    BRUTE_FORCE_STOP_EVENT.set()
    os.kill(os.getpid(), signal.SIGTERM)

