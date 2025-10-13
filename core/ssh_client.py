# -*- UTF-8 -*-
# core/ssh_client.py

import threading
import time
import random
from typing import Optional, Union

from paramiko import SSHClient, AutoAddPolicy, AuthenticationException

from utils.io_utils import IO
from core.config import DEFAULT_PATH


class SSH_CONNECT(SSHClient):  # type: ignore[name-defined]
    """Paramiko SSHClient subclass with hardened connect and safe exec."""

    def __init__(self, username: str, password: str, timeout: int) -> None:
        super().__init__()
        self.set_missing_host_key_policy(AutoAddPolicy())
        self._username = username
        self._password = password
        self._timeout = timeout

    def __enter__(self) -> "SSH_CONNECT":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.close()

    def connect(self, hostname, port=22):  # noqa: ANN001
        attempts = 0
        last_exc: Optional[Exception] = None
        while attempts < 3:
            attempts += 1
            try:
                super().connect(
                    hostname=hostname,
                    port=int(port),
                    username=self._username,
                    password=self._password,
                    look_for_keys=False,
                    allow_agent=False,
                    timeout=self._timeout,
                    auth_timeout=self._timeout,
                    banner_timeout=self._timeout,
                )
                return
            except Exception as exc:
                last_exc = exc
                msg = str(exc).lower()
                retryable = any(k in msg for k in (
                    "error reading ssh protocol banner",
                    "ssh exception",
                    "no existing session",
                    "socket is closed",
                    "timed out",
                    "timeout",
                    "connection reset",
                    "no valid connections",
                ))
                if attempts < 3 and retryable:
                    time.sleep(0.1 * attempts + random.uniform(0, 0.1))
                    continue
                break
        raise RuntimeError(f"connect failed {hostname}:{port}: {last_exc}")