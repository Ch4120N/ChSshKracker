from __future__ import annotations

from typing import List

from ..models import HoneypotDetector, ServerInfo
from ..ssh.client import SSHClient


def detect_honeypot(client: SSHClient, server: ServerInfo, detector: HoneypotDetector) -> bool:
    score = 0
    score += analyze_command_output(server)
    if detector.time_analysis:
        score += analyze_response_time(server)
    score += analyze_file_system(server)
    score += analyze_processes(server)
    if detector.network_analysis:
        score += analyze_network(client)
    score += behavioral_tests(client, server)
    score += detect_anomalies(server)
    score += advanced_tests(client)
    score += performance_tests(client)
    server.honeypot_score = score
    return score >= 6


def _lower(text: str) -> str:
    return text.lower() if text else ""


def analyze_command_output(server: ServerInfo) -> int:
    score = 0
    indicators: List[str] = [
        "fake", "simulation", "honeypot", "trap", "monitor",
        "cowrie", "kippo", "artillery", "honeyd", "ssh-honeypot", "honeytrap",
        "/opt/honeypot", "/var/log/honeypot", "/usr/share/doc/*/copyright",
    ]
    for out in server.commands.values():
        low = _lower(out)
        for ind in indicators:
            if ind in low:
                score += 3
    return score


def analyze_response_time(server: ServerInfo) -> int:
    if server.response_time is None:
        return 0
    if server.response_time.total_seconds() * 1000 < 10:
        return 2
    return 0


def analyze_file_system(server: ServerInfo) -> int:
    score = 0
    ls_output = server.commands.get("ls_root", "")
    if not ls_output:
        return 0
    suspicious = ["total 0", "total 4", "honeypot", "fake", "simulation"]
    low = _lower(ls_output)
    for pat in suspicious:
        if pat in low:
            score += 1
    lines = [ln for ln in ls_output.strip().splitlines() if ln.strip()]
    if len(lines) < 5:
        score += 1
    return score


def analyze_processes(server: ServerInfo) -> int:
    score = 0
    ps_output = server.commands.get("ps", "")
    if not ps_output:
        return 0
    suspicious = [
        "cowrie", "kippo", "honeypot", "honeyd",
        "artillery", "honeytrap", "glastopf",
        "python honeypot", "perl honeypot",
    ]
    low = _lower(ps_output)
    for proc in suspicious:
        if proc in low:
            score += 2
    lines = [ln for ln in ps_output.strip().splitlines() if ln.strip()]
    if len(lines) < 5:
        score += 1
    return score


def analyze_network(client: SSHClient) -> int:
    score = 0
    network_cfg = client.exec("ls -la /etc/network/interfaces /etc/sysconfig/network-scripts/ /etc/netplan/ 2>/dev/null | head -5")
    low = _lower(network_cfg)
    if "total 0" in low or "no such file" in low or len(network_cfg.strip()) < 10:
        score += 1
    iface = client.exec("ip addr show 2>/dev/null | grep -E '^[0-9]+' | head -5")
    low = _lower(iface)
    if any(k in low for k in ("fake", "honeypot", "trap")) or len(iface.strip()) < 10:
        score += 1
    route = client.exec("ip route show 2>/dev/null | head -3")
    if len(route.strip()) < 20:
        score += 1
    return score


def behavioral_tests(client: SSHClient, server: ServerInfo) -> int:
    score = 0
    # create tmp file
    tmp = f"/tmp/test_{id(server)}"
    create_out = client.exec(f"echo 'test' > {tmp}")
    low = _lower(create_out)
    if "error" in low or "permission denied" in low:
        score += 1
    else:
        client.exec(f"rm -f {tmp}")

    sensitive = ["/etc/passwd", "/etc/shadow", "/proc/version"]
    accessible = 0
    for path in sensitive:
        out = client.exec(f"cat {path} 2>/dev/null | head -1")
        low = _lower(out)
        if "error" not in low and out.strip():
            accessible += 1
    if accessible == len(sensitive):
        score += 1

    cmds = ["id", "whoami", "pwd"]
    ok = 0
    for c in cmds:
        out = client.exec(c)
        if "error" not in _lower(out) and out.strip():
            ok += 1
    if ok == 0:
        score += 2
    return score


def advanced_tests(client: SSHClient) -> int:
    score = 0
    cpu = client.exec("cat /proc/cpuinfo | grep 'model name' | head -1")
    low = _lower(cpu)
    if "qemu" in low or "virtual" in low:
        score += 1
    kernel = client.exec("uname -r")
    if "generic" in kernel and len(kernel.strip()) < 20:
        score += 1
    pms = ["which apt", "which yum", "which pacman", "which zypper"]
    found = 0
    for pm in pms:
        out = client.exec(pm)
        if "not found" not in out and out.strip():
            found += 1
    if found == 0:
        score += 1
    services = client.exec("systemctl list-units --type=service --state=running 2>/dev/null | head -10")
    if "0 loaded units" in services or len(services.strip()) < 50:
        score += 1
    internet = client.exec("ping -c 1 8.8.8.8 2>/dev/null | grep '1 packets transmitted'")
    if not internet.strip():
        score += 1
    return score


def performance_tests(client: SSHClient) -> int:
    score = 0
    io_test = client.exec("time dd if=/dev/zero of=/tmp/test bs=1M count=10 2>&1")
    if "command not found" in io_test:
        score += 1
    client.exec("rm -f /tmp/test")
    network_test = client.exec("ss -tuln 2>/dev/null | wc -l")
    try:
        count = int(network_test.strip()) if network_test.strip() else 0
        if count < 5:
            score += 1
    except ValueError:
        pass
    return score


def detect_anomalies(server: ServerInfo) -> int:
    score = 0
    if server.hostname:
        suspicious = [
            "honeypot", "fake", "trap", "monitor", "sandbox",
            "test", "simulation", "gnu/linux", "preempt_dynamic",
        ]
        low = server.hostname.lower()
        for s in suspicious:
            if s in low:
                score += 1
    uptime = server.commands.get("uptime", "")
    if uptime:
        low = uptime.lower()
        if ("0:" in uptime) or ("min" in low) or ("command not found" in low):
            score += 1
    history = server.commands.get("history", "")
    if history:
        lines = [ln for ln in history.strip().splitlines() if ln.strip()]
        if len(lines) < 3:
            score += 1
    return score

