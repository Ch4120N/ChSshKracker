from __future__ import annotations

from ChSSHKracker.cli import build_tasks


def test_build_tasks(tmp_path):
    combo = tmp_path / "combo.txt"
    ips = tmp_path / "ips.txt"
    combo.write_text("user:pass\nroot:toor\n", encoding="utf-8")
    ips.write_text("1.2.3.4:22\n5.6.7.8:2222\n", encoding="utf-8")

    tasks = build_tasks(str(combo), str(ips))
    # 2 combos x 2 ips = 4 tasks
    assert len(tasks) == 4
    assert any(t.username == "root" and t.password == "toor" for t in tasks)

