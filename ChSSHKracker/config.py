from dataclasses import dataclass


@dataclass
class AppConfig:
    timeout_seconds: int
    max_workers: int
    concurrent_per_worker: int
    ip_file: str
    username_file: str
    password_file: str


CONCURRENT_PER_WORKER = 25

