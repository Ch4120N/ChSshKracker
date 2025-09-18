from __future__ import annotations

import random
from pathlib import Path


def generate_ips(count: int = 10, port: int = 22) -> list[str]:
    ips: list[str] = []
    for _ in range(count):
        a = random.randint(1, 223)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        d = random.randint(1, 254)
        ips.append(f"{a}.{b}.{c}.{d}:{port}")
    return ips


def write_ips(path: str, ips: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(ips) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test IP:port list")
    parser.add_argument("--out", default="tests/data/ips.txt")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--port", type=int, default=22)
    args = parser.parse_args()

    ips = generate_ips(args.count, args.port)
    write_ips(args.out, ips)
    print(f"Wrote {len(ips)} IPs to {args.out}")

