from __future__ import annotations

from pathlib import Path
from typing import Iterable, List


def read_items(path: str) -> List[List[str]]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    items: List[List[str]] = []
    with file_path.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            items.append(line.split(":"))
    return items


def write_combo_file(usernames: Iterable[Iterable[str]], passwords: Iterable[Iterable[str]], out_path: str) -> None:
    out = Path(out_path)
    with out.open("w", encoding="utf-8") as fh:
        for u in usernames:
            for p in passwords:
                fh.write(f"{u[0]}:{p[0]}\n")


def append_text(data: str, filepath: str) -> None:
    out = Path(filepath)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as fh:
        fh.write(data)

