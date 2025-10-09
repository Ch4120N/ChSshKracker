# -*- UTF-8 -*-
# utils/io_utils.py

from pathlib import Path
from typing import List, Tuple

from ui.decorators import MsgDCR

class IO:
    @staticmethod
    def read_lines(path: Path) -> List[str]:
        """Read non-empty, stripped lines from a file."""
        try:
            with path.open('r', encoding='utf-8', errors='ignore') as file_read:
                return [line.strip() for line in file_read if line.strip()]
        except Exception:
            MsgDCR.FailureMessage(f"Failed to read file: {path}")
            return []

    @staticmethod
    def file_append(path: Path, data: str) -> None:
        """Append data to file, creating it if needed; swallow I/O errors to keep pipeline running."""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)  # Make sure directory exists
            with path.open(mode="a", encoding="utf-8", errors="ignore") as file_append:
                file_append.write(data)
        except Exception:
            MsgDCR.FailureMessage(f"Failed writing to: {path}")

    @staticmethod
    def create_combo_file(user_file: Path, pass_file: Path, combo_path: Path) -> None:
        """Generate username:password combinations and persist to combo file."""
        usernames = IO.read_lines(user_file)
        passwords = IO.read_lines(pass_file)
        try:
            combo_path.parent.mkdir(parents=True, exist_ok=True)  # Make sure directory exists
            with combo_path.open(mode="w", encoding="utf-8", errors="ignore") as combo_file:
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
