# -*- UTF-8 -*-
# utils/io_utils.py

import os
from pathlib import Path
from typing import List, Tuple

from ui.decorators import MsgDCR

class IO:
    @staticmethod
    def read_lines(path: str) -> List[str]:
        """Read non-empty, stripped lines from a file."""
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as file_read:
                return [line.strip() for line in file_read if line.strip()]
        except Exception:
            MsgDCR.FailureMessage(f"Failed to read file: {path}")
            return []

    @staticmethod
    def file_append(path: str, data: str) -> None:
        """Append data to file, creating it if needed; swallow I/O errors to keep pipeline running."""
        try:
            path_dir = os.path.dirname(path)
            if (not os.path.exists(path_dir)):
                os.makedirs(path_dir, exist_ok=True)
            with open(path, mode="a", encoding="utf-8", errors="ignore") as file_append:
                file_append.write(data)
        except Exception:
            MsgDCR.FailureMessage(f"Failed writing to: {path}")

    @staticmethod
    def create_combo_file(user_file: str, pass_file: str, combo_path: str) -> None:
        """Generate username:password combinations and persist to combo file."""
        usernames = IO.read_lines(user_file)
        passwords = IO.read_lines(pass_file)
        try:
            combo_dir = os.path.dirname(combo_path)
            if (not os.path.exists(combo_path)):
                os.makedirs(combo_dir, exist_ok=True)
            with open(combo_path, mode="w", encoding="utf-8", errors="ignore") as combo_file:
                for u in usernames:
                    for p in passwords:
                        combo_file.write(f"{u}:{p}\n")
        except Exception:
            MsgDCR.FailureMessage(f"Failed to create combo file: {combo_path}")

    @staticmethod
    def parse_combo(path: Path) -> List[Tuple[str, str]]:
        """Parse combo file of username:password into tuples."""
        lines = IO.read_lines(path)
        combos: List[Tuple[str, str]] = []
        for line in lines:
            if ":" in line:
                u, p = line.split(":", 1)
                combos.append((u, p))
        return combos

    @staticmethod
    def parse_targets(path: Path) -> List[Tuple[str, str]]:
        """Parse targets file of ip:port into tuples. Missing port defaults to 22."""
        lines = IO.read_lines(path)
        targets: List[Tuple[str, str]] = []
        for line in lines:
            if ":" in line:
                ip, port = line.rsplit(":", 1)
                targets.append((ip.strip(), port.strip()))
            else:
                targets.append((line.strip(), "22"))
        return targets
