# -*- UTF-8 -*-
# core/ssh_client.py

import threading
import socket
from typing import Optional, Union

import lib.SSH as SSH

class SSH_CONNECT(SSH.SSHClient):
    def __init__(
        self,
        hostname: str,
        port: int = 22,
        username: Optional[str] = None,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        timeout: Optional[Union[int, float]] = 30,
        **kwargs
    ):
        super().__init__()
        self.set_missing_host_key_policy(SSH.AutoAddPolicy())

        self._hostname = hostname
        self._port = port
        self._username = username
        self._password = password
        self._key_filename = key_filename
        self._timeout = timeout
        self._kwargs = kwargs

        self._lock = threading.RLock()
        self._connected = False

    def connect_safe(self) -> bool:
        with self._lock:
            if self._connected:
                return True

            try:
                super().connect(
                    hostname=self._hostname,
                    port=self._port,
                    username=self._username,
                    password=self._password,
                    key_filename=self._key_filename,
                    look_for_keys=False,
                    allow_agent=False,
                    timeout=self._timeout,
                    **self._kwargs
                )
                self._connected = True
                return True
            except (
                Exception,
                EOFError,
                OSError,
                socket.error, 
                socket.timeout, 
                SSH.AuthenticationException, 
                SSH.BadAuthenticationType,
                SSH.BadHostKeyException,
                SSH.SSHException,
                SSH.ssh_exception.SSHException
                ):
                self._connected = False
                return False

    def run(self, command: str, timeout: Optional[Union[int, float]] = None) -> str:
        with self._lock:
            if not self._connected:
                return "ERROR: Not connected"

            try:
                actual_timeout = timeout if timeout is not None else self._timeout
                stdin, stdout, stderr = self.exec_command(command, timeout=actual_timeout)
                out = stdout.read().decode(errors="ignore")
                err = stderr.read().decode(errors="ignore")

                if err.strip():
                    return f"ERROR: {err.strip()}"
                return out
            except Exception as exc:
                return f"ERROR: {exc}"

    def close(self):
        with self._lock:
            try:
                super().close()
                self._connected = False
                return True
            except Exception:
                return False
    def __enter__(self):
        """Auto-connect when entering 'with' block."""
        if not self.connect_safe():
            raise ConnectionError(f"Failed to connect to {self._hostname}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Auto-close when leaving 'with' block."""
        self.close()
