from __future__ import annotations

import socket
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator, Optional

import paramiko


class SSHClient:
    def __init__(self, host: str, port: int, username: str, password: str, timeout_seconds: int) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout_seconds
        self._client: Optional[paramiko.SSHClient] = None

    def connect(self) -> None:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=self.timeout,
                banner_timeout=self.timeout,
                auth_timeout=self.timeout,
                look_for_keys=False,
                allow_agent=False,
            )
        except (socket.timeout, paramiko.SSHException, OSError) as exc:
            raise exc
        self._client = client

    def close(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            finally:
                self._client = None

    @contextmanager
    def session(self) -> Iterator[paramiko.SSHClient]:
        if self._client is None:
            raise RuntimeError("SSH client is not connected")
        try:
            yield self._client
        finally:
            pass

    def exec(self, command: str) -> str:
        if self._client is None:
            raise RuntimeError("SSH client is not connected")
        try:
            _, stdout, stderr = self._client.exec_command(command, timeout=self.timeout)
            out = stdout.read().decode(errors="ignore")
            err = stderr.read().decode(errors="ignore")
            if err and not out:
                return f"ERROR: {err.strip()}"
            return out or err
        except Exception as exc:  # keep behavior similar to Go code
            return f"ERROR: {exc}"

