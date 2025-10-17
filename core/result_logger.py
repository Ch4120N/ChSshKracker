# -*- coding: utf-8 -*-
# core/result_logger.py

import time

from core.config import FILE_PATH
from core.models import ServerInfo
from utils.file_manager import FileManager
from ui.table import Table


class ResultLogger:
    def __init__(self):
        self.file_manager = FileManager()
        self.goods_file = FILE_PATH.GOODS_FILE
        self.goods_detailed_file = FILE_PATH.DETAILED_FILE
        self.honeypot_file = FILE_PATH.HONEYPOT_FILE
        self.debug_file = FILE_PATH.DEBUG_FILE
    
    def log_success(self, server: ServerInfo) -> None:
        simple = f"{server.ip}:{server.port}@{server.username}:{server.password}"
        self.file_manager.file_append(self.goods_file, simple + "\n")
        detailed_table = Table(block_padding=4)
        detailed_table.add_block(['SSH SUCCESS'])
        detailed_table.add_block([
            f'Target: {server.ip}:{server.port}',
            f'Credentials: {server.username}:{server.password}',
            f'Hostname: {server.hostname}',
            f'OS: {server.os_info}',
            f'SSH Version: {server.ssh_version}',
            f'Response Time: {server.response_time_ms:.2f} ms',
            f'Open Ports: {server.open_ports}',
            f'Honeypot Score: {server.honeypot_score}',
            f'Timestamp: {(time.strftime("%Y-%m-%d %H:%M:%S"))}'
        ])
        self.file_manager.file_append(self.goods_detailed_file,
                    detailed_table.display_plain() + '\n')
    
    def log_honeypot(self, server: ServerInfo):
        simple = f"{server.ip}:{server.port}@{server.username}:{server.password}"
        honeypot_info = (
            f'HONEYPOT: {simple} '
            f'(Score: {server.honeypot_score})\n'
        )
        self.file_manager.file_append(self.honeypot_file, honeypot_info)
    
    def log_debug_file(self, RequestsMessage: str):
        self.file_manager.file_append(self.debug_file, RequestsMessage)