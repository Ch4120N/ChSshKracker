from __future__ import annotations

from datetime import datetime
from typing import Iterable

from ..models import ServerInfo
from .files import append_text


def log_success(server: ServerInfo) -> None:
    success_message = f"{server.ip}:{server.port}@{server.username}:{server.password}"
    append_text(success_message + "\n", "su-goods.txt")

    detailed = (
        "\n=== \U0001F3AF SSH Success \U0001F3AF ===\n"
        f"\U0001F310 Target: {server.ip}:{server.port}\n"
        f"\U0001F511 Credentials: {server.username}:{server.password}\n"
        f"\U0001F5A5\uFE0F Hostname: {server.hostname}\n"
        f"\U0001F427 OS: {server.os_info}\n"
        f"\U0001F4E1 SSH Version: {server.ssh_version}\n"
        f"\u26A1 Response Time: {server.response_time}\n"
        f"\U0001F50C Open Ports: {server.open_ports}\n"
        f"\U0001F36F Honeypot Score: {server.honeypot_score}\n"
        f"\U0001F559 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "========================\n"
    )
    append_text(detailed, "detailed-results.txt")
    print(f"\u2705 SUCCESS: {success_message}")


def log_honeypot(server: ServerInfo) -> None:
    append_text(
        f"HONEYPOT: {server.ip}:{server.port}@{server.username}:{server.password} (Score: {server.honeypot_score})\n",
        "honeypots.txt",
    )

