from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List


@dataclass
class SSHTask:
    ip: str
    port: str
    username: str
    password: str


@dataclass
class ServerInfo:
    ip: str
    port: str
    username: str
    password: str
    is_honeypot: bool = False
    honeypot_score: int = 0
    ssh_version: str = ""
    os_info: str = ""
    hostname: str = ""
    response_time: timedelta | None = None
    commands: Dict[str, str] = field(default_factory=dict)
    open_ports: List[str] = field(default_factory=list)


@dataclass
class HoneypotDetector:
    time_analysis: bool = True
    command_analysis: bool = True
    network_analysis: bool = True

