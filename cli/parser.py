# -*- UTF-8 -*-
# cli/parser.py

import argparse
from typing import Callable

from colorama import Fore, init
init(autoreset=True)

from core.config import (
    __version__,
    SCRIPT_NAME,
    SCRIPT_DESCRIPTION,
    globalConfig
)
from ui.sharp_box import SharpBox
from ui.banner import Banners
from cli.formatter import HelpFormatter


class Parser:
    def build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=SCRIPT_NAME,
            description=SCRIPT_DESCRIPTION,
            formatter_class=HelpFormatter,
            add_help=False,
        )
        parser.add_argument("-U", "--user-list", type=str,
                            help="Path to usernames file (one per line)", dest="user_list")
        parser.add_argument("-P", "--password-list", type=str,
                            help="Path to passwords file (one per line)", dest="password_list")
        parser.add_argument("-I", "--ip-list", type=str,
                            help="Path to targets file (ip[:port] per line)", dest="ip_list")
        parser.add_argument("-C", "--combo-list", type=str,
                            help="Generated combo file path", dest="combo_list")
        parser.add_argument("-t", "--timeout", type=int, default=globalConfig.TIMEOUT_SECS,
                            help="Connection timeout seconds", dest="timeout")
        parser.add_argument("-w", "--workers", type=int, default=globalConfig.MAX_WORKERS,
                            help="Max number of workers", dest="workers")
        parser.add_argument("--per-worker", type=int, default=globalConfig.CONCURRENT_PER_WORKER,
                            help="Concurrent connections per worker", dest="per_worker")
        parser.add_argument("--interactive", action="store_true",
                            help="Force interactive prompts", dest="interactive")
        parser.add_argument("-v", "--version", action="version", version=f"{Fore.LIGHTCYAN_EX}\n [ {Fore.LIGHTWHITE_EX}*{Fore.LIGHTCYAN_EX} ] {Fore.LIGHTWHITE_EX}%(prog)s{Fore.LIGHTRED_EX} v{__version__}",
                            help="Shows script version and exit", dest="version")
        return parser

    def render_help() -> str:
        title = f"{SCRIPT_NAME} - Advanced Ch4120N SSH Brute Force Tool"
        version = __version__
        description = SCRIPT_DESCRIPTION
        usage = 'Usage: python ChSshKracker.py [OPTIONS]'
        options = [
            ('-h, --help', 'Show this help message and exit'),
            ('-v, --version', 'Show script version and exit'),
            ('-I, --ip-list', 'Path to targets file (ip[:port] per line)'),
            ('-U, --user-list', 'Path to usernames file (one per line)'),
            ('-P, --password-list', 'Path to passwords file (one per line)'),
            ('-C, --combo-list', 'Generated combo file path'),
            ('-t, --timeout', 'Connection timeout seconds (default: 5)'),
            ('-w, --workers', 'Max number of workers (default: 10)'),
            ('--per-worker', 'Concurrent connections per worker (default: 25. Recommended)'),
            ('--interactive', 'Force interactive prompts')
        ]
        examples = [
            'python ChSshKracker.py -I ips.txt -U users.txt -P password.txt',
            'python ChSshKracker.py -I ips.txt -U users.txt -P password.txt -w 50 -t 10',
            'python ChSshKracker.py -I ips.txt -C combo.txt -w 50 -t 10 --per-worker 30'
        ]
        banner = SharpBox(title=title, version=version, description=description, usage=usage,
                        options=options, examples=examples, width=106, margin_left=2)
        return (Fore.LIGHTRED_EX + Banners.MainBanner(7) + Fore.RESET + '\n' + banner.render())
