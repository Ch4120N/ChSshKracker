from __future__ import annotations

from typing import Dict

from ..models import ServerInfo
from .client import SSHClient
from .commands import DEFAULT_COMMANDS, run_commands, scan_local_ports


def gather_system_info(client: SSHClient, server: ServerInfo) -> None:
    outputs: Dict[str, str] = run_commands(client, DEFAULT_COMMANDS)
    server.commands.update(outputs)

    server.hostname = outputs.get("hostname", "").strip()
    server.os_info = outputs.get("uname", "").strip()
    server.ssh_version = outputs.get("ssh_version", "").strip()

    server.open_ports = scan_local_ports(client)

