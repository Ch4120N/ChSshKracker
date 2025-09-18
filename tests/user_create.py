from __future__ import annotations

from pathlib import Path


def generate_users() -> list[str]:
    return [
        "root",
        "admin",
        "user",
        "test",
        "ubuntu",
        "ec2-user",
        "pi",
    ]


def write_users(path: str, users: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(users) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test usernames list")
    parser.add_argument("--out", default="tests/data/users.txt")
    args = parser.parse_args()

    users = generate_users()
    write_users(args.out, users)
    print(f"Wrote {len(users)} users to {args.out}")

