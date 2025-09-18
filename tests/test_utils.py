from __future__ import annotations

from chsshkracker.utils.time_utils import format_duration
from chsshkracker.utils.files import read_items


def test_format_duration_basic():
    assert format_duration(0) == "00:00:00:00"
    assert format_duration(59) == "00:00:00:59"
    assert format_duration(60) == "00:00:01:00"
    assert format_duration(3600) == "00:01:00:00"


def test_read_items(tmp_path):
    p = tmp_path / "sample.txt"
    p.write_text("user:pass\nadmin:admin\n\n", encoding="utf-8")
    items = read_items(str(p))
    assert items == [["user", "pass"], ["admin", "admin"]]

