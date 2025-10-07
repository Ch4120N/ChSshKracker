# -*- UTF-8 -*-
# core/ssh_client.py

import random
import time
from typing import Optional

import paramiko

class SSH_CONNECT(paramiko.SSHClient):
    def __init__(self, username: str, password: str, timeout: int) -> None:
        super().__init__()
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._username = username
        self._password = password
        self._timeout = timeout

    def __enter__(self) -> "SSH_CONNECT":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.close()

    def connect(self, hostname, port=22, username=None, password=None, *args, **kwargs):  # noqa: ANN001
        attempts = 0
        last_exc: Optional[Exception] = None
        while attempts < 3:
            attempts += 1
            try:
                # sock = socket.create_connection(
                #     (hostname, int(port)), timeout=self._timeout)
                # sock.settimeout(self._timeout)
                # with contextlib.suppress(Exception):
                #     sock.recv(128, socket.MSG_PEEK)
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
                retry_able = any(k in msg for k in (
                    "error reading ssh protocol banner",
                    "ssh exception",
                    "no existing session",
                    "socket is closed",
                    "timed out",
                    "timeout",
                    "connection reset",
                    "no valid connections",
                ))
                if attempts < 3 and retry_able:
                    time.sleep(0.1 * attempts + random.uniform(0, 0.1))
                    continue
                break
        raise RuntimeError(f"connect failed {hostname}:{port}: {last_exc}")

    def run(self, command: str) -> str:
        try:
            stdin, stdout, stderr = self.exec_command(
                command, timeout=self._timeout)
            out = stdout.read().decode(errors="ignore")
            err = stderr.read().decode(errors="ignore")
            if err.strip():
                return f"ERROR: {err.strip()}"
            return out
        except Exception as exc:
            return f"ERROR: {exc}"