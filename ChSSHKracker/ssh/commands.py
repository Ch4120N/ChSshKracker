from __future__ import annotations

from typing import Dict, List

from .client import SSHClient


DEFAULT_COMMANDS: Dict[str, str] = {
    "hostname": "hostname",
    "uname": "uname -a",
    "whoami": "whoami",
    "pwd": "pwd",
    "ls_root": "ls -la /",
    "ps": "ps aux | head -10",
    "netstat": "netstat -tulpn | head -10",
    "history": "history | tail -5",
    "ssh_version": "ssh -V",
    "uptime": "uptime",
    "mount": "mount | head -5",
    "env": "env | head -10",
}


def run_commands(client: SSHClient, commands: Dict[str, str]) -> Dict[str, str]:
    results: Dict[str, str] = {}
    for key, cmd in commands.items():
        results[key] = client.exec(cmd)
    return results


def scan_local_ports(client: SSHClient) -> List[str]:
    output = client.exec("netstat -tulpn 2>/dev/null | grep LISTEN | head -20")
    ports: List[str] = []
    for line in output.splitlines():
        parts = line.split()
        for part in parts:
            if ":" in part:
                maybe = part.rsplit(":", 1)[-1]
                if maybe.isdigit() and maybe not in ports:
                    ports.append(maybe)
    return ports

