from dataclasses import dataclass
import os
import psutil


@dataclass
class AppConfig:
    timeout_seconds: int
    max_workers: int
    concurrent_per_worker: int
    ip_file: str
    username_file: str
    password_file: str
    max_memory_mb: int = 512
    max_cpu_percent: float = 80.0
    adaptive_workers: bool = True


CONCURRENT_PER_WORKER = 25


def get_optimal_worker_count() -> int:
    """Calculate optimal worker count based on system resources"""
    try:
        # Get CPU count and available memory
        cpu_count = os.cpu_count() or 4
        memory_gb = psutil.virtual_memory().available / (1024**3)
        
        # Conservative limits to prevent system overload
        max_workers_by_cpu = min(cpu_count * 2, 50)  # Max 2 workers per CPU core
        max_workers_by_memory = int(memory_gb * 2)  # 2 workers per GB RAM
        
        # Use the more restrictive limit
        optimal = min(max_workers_by_cpu, max_workers_by_memory, 20)
        return max(1, optimal)
    except Exception:
        return 4  # Safe fallback


def get_optimal_concurrent_per_worker() -> int:
    """Calculate optimal concurrent connections per worker"""
    try:
        memory_gb = psutil.virtual_memory().available / (1024**3)
        if memory_gb < 1:
            return 5
        elif memory_gb < 2:
            return 10
        elif memory_gb < 4:
            return 15
        else:
            return 20  # Reduced from 25
    except Exception:
        return 10

