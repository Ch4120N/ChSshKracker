from __future__ import annotations

import math


def format_duration(seconds: float) -> str:
    days = int(seconds) // 86400
    hours = (int(seconds) % 86400) // 3600
    minutes = (int(seconds) % 3600) // 60
    secs = int(math.fmod(seconds, 60))
    return f"{days:02d}:{hours:02d}:{minutes:02d}:{secs:02d}"

