# -*- UTF-8 -*-
# ChSshKracker.py

import os
import sys
import signal
try:
    import paramiko
    from colorama import Fore, init
    from prompt_toolkit import prompt
    init(autoreset=True)
except ImportError:
    sys.exit('\n [ - ] Please install requirements libraries. Using commands below:\n' \
             '\t- python -m pip install cryptography==40.0.2 paramiko==3.4.0 colorama==0.4.6 prompt_toolkit==3.0.52\n' \
             '\t- Or\n' \
             '\t- python -m pip install -r requirements.txt\n'
            )

from core.config import (
    globalConfig,
    FILES_PATH,
    DEFAULT_PATH,
    SUMMARY
)
from utils.io_utils import IO
from ui.decorators import MsgDCR
from ui.summary_render import SummaryRenderer
from cli.interactive import InteractiveUI, Inputs
from cli.parser import Parser
from cli.signals import handle_SIGINT


class ChSSHKracker:
    def __init__(self):
        signal.signal(signal.SIGINT, handle_SIGINT)

        self.summary_obj = SummaryRenderer(
            title='Configuration Summary', 
            space=5, 
            margin_left_spaces=2,
            max_width=80
        )
        self.parser_obj = Parser()
    
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

        if (not interactive_flag and (ip_list and combo_list or user_list or password_list)):
            if ((not os.path.isfile(ip_list)) or (not os.path.exists(ip_list))):
                MsgDCR.FailureMessage(f'IP list does not exist: {ip_list}')
                sys.exit(2)

            if (combo_list):
                if ((not os.path.isfile(combo_list)) or (not os.path.exists(combo_list))):
                    MsgDCR.FailureMessage(f'Combo list does not exist: {combo_list}')
                    sys.exit(2)
                combo_list_path = os.path.realpath(combo_list)
                try:
                    self.parse_combos = IO.parse_combo(combo_list_path)
                except Exception:
                    MsgDCR.FailureMessage('Error on loading combo list')
                    sys.exit(2)
                SUMMARY['USE COMBO'] = 'YES'
                SUMMARY['COMBO FILE'] = combo_list_path
                FILES_PATH.COMBO_FILE = combo_list_path
            
            else:
                SUMMARY['USE COMBO'] = 'No'
                SUMMARY['COMBO FILE'] = DEFAULT_PATH.COMBO_FILE
                FILES_PATH.COMBO_FILE = DEFAULT_PATH.COMBO_FILE

                if (user_list):
                    if ((not os.path.isfile(user_list)) or (not os.path.exists(user_list))):
                        MsgDCR.FailureMessage(f'Username list does not exist: {user_list}')
                        sys.exit(2)
                else:
                    MsgDCR.FailureMessage('Username list is required if your not using combo file')
                    sys.exit(1)

                if (password_list):
                    if ((not os.path.isfile(password_list)) or (not os.path.exists(password_list))):
                        MsgDCR.FailureMessage(f'Password list does not exist: {password_list}')
                        sys.exit(2)
                else:
                    MsgDCR.FailureMessage('Password list is required if your not using combo file')
                    sys.exit(1)

            if (timeout):
                if (int(timeout) < 1):
                    MsgDCR.FailureMessage('Please enter valid positive integer for timeout')
                    sys.exit(2)
                globalConfig.TIMEOUT_SECS = timeout
                SUMMARY['TIMEOUT (S)'] = timeout
            
            if (max_workers):
                if (int(max_workers) < 1):
                    MsgDCR.FailureMessage('Please enter valid positive integer for workers')
                    sys.exit(2)
                globalConfig.MAX_WORKERS = max_workers
                SUMMARY['MAX WORKERS'] = max_workers
            
            if (per_worker):
                if (int(per_worker) < 1):
                    MsgDCR.FailureMessage('Please enter valid positive integer for per worker')
                    sys.exit(2)
                globalConfig.CONCURRENT_PER_WORKER = per_worker
                SUMMARY['PER WORKER'] = per_worker
            
            try:
                user_file_path = os.path.realpath(user_list)
                pass_file_path = os.path.realpath(password_list)
                combo_file_path = os.path.realpath(FILES_PATH.COMBO_FILE)
                SUMMARY['USERNAME FILE'] = user_file_path
                SUMMARY['PASSWORD FILE'] = pass_file_path


                IO.create_combo_file(user_file_path, pass_file_path, combo_file_path)
                MsgDCR.SuccessMessage(f'Combo list created at: {combo_file_path}')
                self.parse_combos = IO.parse_combo(combo_file_path)
                MsgDCR.InfoMessage(f'Total combos loaded from generated combo file: {len(self.parse_combos)}')
            except Exception:
                MsgDCR.FailureMessage('Error on creating combo list')
                sys.exit(1)
            
            try:
                target_ips_path = os.path.realpath(ip_list)
                SUMMARY['IP FILE'] = target_ips_path
                self.parse_target_ips = IO.parse_targets(target_ips_path)
                MsgDCR.InfoMessage(f'Total target IPs loaded from IP list: {len(self.parse_target_ips)}')
            except Exception:
                MsgDCR.FailureMessage('Error on loading IP list')
                sys.exit(1)
        else:
            self.interactive_prompts = InteractiveUI()
            self.interactive_prompts.run()
            

        globalConfig.TOTAL_TASKS = len(
            self.parse_combos) * len(self.parse_target_ips)
        


if __name__ == '__main__':
    ChSSHKracker()