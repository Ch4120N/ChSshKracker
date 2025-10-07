# -*- UTF-8 -*-
# core/config.py

import re
from threading import Event, Lock

__version__ = '1.3.0'
SCRIPT_NAME = 'ChSSHKracker' # Script name
SCRIPT_DESCRIPTION = (
    'A powerful, high-performance SSH brute force tool written in Python 3.9 with enhanced multi-layer worker architecture'
    ', advanced honeypot detection, real-time statistics, and comprehensive system reconnaissance capabilities'
) # Script description

SUMMARY = {
    'IP FILE' : None,
    'USE COMBO' : None,
    'COMBO FILE' : None,
    'USERNAME FILE' : None,
    'PASSWORD FILE' : None,
    'TIMEOUT (S)' : 0,
    'MAX WORKERS' : 0,
    'PER WORKER' : 0
}

BRUTE_FORCE_STOP_EVENT = Event()

class STATS:
    GOODS:int = 0
    ERRORS:int = 0
    HONEYPOTS:int = 0
    STATS_LOCK = Lock()
    SUCCESS_MAP_LOCK = Lock()
    SUCCESSFUL_IP_PORT: set[str] = set()

class DEFAULT_PATH:
    DEBUG_FILE: str               = 'log/debug.log'
    COMBO_FILE: str               = 'data/COMBO.TXT'
    GOODS_FILE: str               = 'data/SSH-GOODS.TXT'
    HONEYPOTS_FILE: str           = 'data/HONEYPOTS.TXT'

class DEFAULT_CONFIG:
    TIMEOUT_SECS: int             = 5
    CONCURRENT_PER_WORKER: int    = 25 # Recommended
    MAX_WORKERS: int              = 25
    START_TIME_MONOTONIC: float   = 0.0


ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')