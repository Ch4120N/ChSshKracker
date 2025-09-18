from __future__ import annotations

from datetime import timedelta

from ChSSHKracker.models import HoneypotDetector, ServerInfo
from ChSSHKracker.detection.honeypot import analyze_command_output, analyze_response_time, detect_anomalies


def test_analyze_command_output_flags_honeypot_keywords():
    srv = ServerInfo(ip="1.2.3.4", port="22", username="u", password="p")
    srv.commands = {"ps": "python cowrie"}
    score = analyze_command_output(srv)
    assert score >= 3


def test_analyze_response_time_fast():
    srv = ServerInfo(ip="1.2.3.4", port="22", username="u", password="p")
    srv.response_time = timedelta(milliseconds=3)
    assert analyze_response_time(srv) >= 2


def test_detect_anomalies_hostname_and_history():
    srv = ServerInfo(ip="1.2.3.4", port="22", username="u", password="p")
    srv.hostname = "test-honeypot"
    srv.commands["history"] = ""
    score = detect_anomalies(srv)
    assert score >= 1

