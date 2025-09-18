from __future__ import annotations

from pathlib import Path


def generate_passwords() -> list[str]:
    return [
        "toor",
        "admin",
        "password",
        "123456",
        "12345678",
        "letmein",
        "qwerty",
        "raspberry",
    ]


def write_passwords(path: str, passwords: list[str]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(passwords) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test passwords list")
    parser.add_argument("--out", default="tests/data/passwords.txt")
    args = parser.parse_args()

    pwds = generate_passwords()
    write_passwords(args.out, pwds)
    print(f"Wrote {len(pwds)} passwords to {args.out}")

