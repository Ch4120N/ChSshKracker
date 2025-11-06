<div align="center">

# ChSSHKracker

## _**Advanced Multi-Threaded SSH Brute Force Tool with Honeypot Detection**_

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/Ch4120N/ChSSHKracker)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

> **A powerful, high-performance SSH brute force tool written in Python with enhanced multi-layer worker architecture, advanced honeypot detection, real-time statistics, and comprehensive system reconnaissance capabilities.**

---

</div>

## 📋 Table of Contents

- [✨ Features](#-features)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [💻 Usage](#-usage)
  - [Command Line Mode](#command-line-mode)
  - [Interactive Mode](#interactive-mode)
- [⚙️ Configuration](#️-configuration)
- [🏗️ Project Structure](#️-project-structure)
- [🔍 Advanced Features](#-advanced-features)
- [📊 Output Files](#-output-files)
- [⚠️ Disclaimer](#️-disclaimer)
- [📄 License](#-license)
- [👤 Programmer](#-Programmer)

---

## ✨ Features

### 🎯 Core Capabilities

- **🚀 High Performance**: Multi-threaded architecture with configurable worker pools
- **🔄 Concurrent Processing**: Multiple concurrent connections per worker for maximum throughput
- **📊 Real-time Statistics**: Live progress tracking with detailed statistics
- **🎨 Beautiful UI**: Colorful terminal interface with ASCII banners and formatted tables
- **📝 Comprehensive Logging**: Detailed logs for successful connections, honeypots, and errors

### 🛡️ Security Features

- **🍯 Advanced Honeypot Detection**: Multi-layer detection system to identify honeypot traps
- **🔍 System Reconnaissance**: Automatic system information gathering after successful connection
- **⏱️ Configurable Timeouts**: Customizable connection timeouts to optimize performance
- **🛑 Graceful Shutdown**: Clean interruption handling with SIGINT support

### 🎮 User Experience

- **💬 Interactive Mode**: User-friendly interactive prompts for easy configuration
- **📁 Flexible Input**: Support for combo files or separate username/password lists
- **🌐 CIDR Support**: Process IP ranges and CIDR notation
- **📈 Progress Tracking**: Real-time progress bars and statistics display

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Ch4120N/ChSSHKracker.git
cd ChSSHKracker

# Install dependencies
pip install -r requirements.txt

# Run in interactive mode
python ChSshKracker.py --interactive

# Or use command line
python ChSshKracker.py -I ips.txt -U users.txt -P passwords.txt
```

---

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Ch4120N/ChSSHKracker.git
   cd ChSSHKracker
   ```

2. **Install required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:

   ```bash
   pip install cryptography==40.0.2 paramiko==2.11.0 colorama==0.4.6 prompt_toolkit==3.0.52
   ```

3. **Verify installation:**
   ```bash
   python ChSshKracker.py --version
   ```

### Dependencies

- `cryptography==40.0.2` - Cryptographic primitives
- `paramiko==2.11.0` - SSH protocol implementation
- `colorama==0.4.6` - Cross-platform colored terminal text
- `prompt_toolkit==3.0.52` - Interactive command-line interface

---

## 💻 Usage

### Command Line Mode

#### Basic Usage

```bash
# Using separate username and password files
python ChSshKracker.py -I ips.txt -U users.txt -P passwords.txt

# Using combo file (username:password format)
python ChSshKracker.py -I ips.txt -C combo.txt

# With custom timeout and workers
python ChSshKracker.py -I ips.txt -U users.txt -P passwords.txt -t 10 -w 50

# Advanced: Custom workers and concurrent connections per worker
python ChSshKracker.py -I ips.txt -C combo.txt -w 50 --per-worker 30 -t 10
```

#### Command Line Arguments

| Argument          | Short | Description                               | Default    |
| ----------------- | ----- | ----------------------------------------- | ---------- |
| `--ip-list`       | `-I`  | Path to targets file (ip[:port] per line) | Required   |
| `--user-list`     | `-U`  | Path to usernames file (one per line)     | Required\* |
| `--password-list` | `-P`  | Path to passwords file (one per line)     | Required\* |
| `--combo-list`    | `-C`  | Generated combo file path                 | Optional   |
| `--timeout`       | `-t`  | Connection timeout in seconds             | 5          |
| `--workers`       | `-w`  | Maximum number of worker threads          | 25         |
| `--per-worker`    |       | Concurrent connections per worker         | 25         |
| `--interactive`   |       | Force interactive prompts                 | False      |
| `--version`       | `-v`  | Show version and exit                     | -          |
| `--help`          | `-h`  | Show help message                         | -          |

\* Required if not using combo file

#### Input File Formats

**IP List (`ips.txt`):**

```
192.168.1.1:22
192.168.1.2:2222
192.168.1.5:8022
```

**Username List (`users.txt`):**

```
root
admin
user
test
```

**Password List (`passwords.txt`):**

```
password
123456
admin
root
```

**Combo File (`combo.txt`):**

```
root:password
admin:admin123
user:password123
```

### Interactive Mode

Launch the interactive mode for a guided setup:

```bash
python ChSshKracker.py --interactive
```

The interactive mode will prompt you for:

- IP list file path
- Username/password files or combo file
- Timeout settings
- Worker configuration
- Concurrent connections per worker

---

## ⚙️ Configuration

### Default Settings

The tool uses the following default configurations (defined in `core/config.py`):

```python
TIMEOUT = 5                    # Connection timeout in seconds
MAX_WORKERS = 25               # Maximum worker threads
CONCURRENT_PER_WORKER = 25     # Concurrent connections per worker
```

### Performance Tuning

**For High-Speed Networks:**

```bash
python ChSshKracker.py -I ips.txt -C combo.txt -w 100 --per-worker 50 -t 3
```

**For Slow/Unstable Networks:**

```bash
python ChSshKracker.py -I ips.txt -C combo.txt -w 10 --per-worker 5 -t 15
```

**Balanced (Recommended):**

```bash
python ChSshKracker.py -I ips.txt -C combo.txt -w 25 --per-worker 25 -t 5
```

---

## 🏗️ Project Structure

```
ChSSHKracker/
│
├── ChSshKracker.py           # Main entry point
├── requirements.txt          # Python dependencies
├── README.MD                 # This file
│
├── core/                     # Core functionality
│   ├── config.py             # Configuration and constants
│   ├── worker.py             # Multi-threaded worker implementation
│   ├── ssh_client.py         # SSH connection handler
│   ├── honeypot.py           # Honeypot detection engine
│   ├── recon.py              # System reconnaissance
│   ├── result_logger.py      # Result logging system
│   ├── stats.py              # Statistics tracking
│   ├── counter.py            # Progress counter
│   └── models.py             # Data models
│
├── cli/                      # Command-line interface
│   ├── parser.py             # Argument parser
│   ├── interactive.py        # Interactive mode
│   ├── formatter.py          # Help formatter
│   └── path_completer.py     # Path autocompletion
│
├── ui/                       # User interface components
│   ├── banner.py             # ASCII banners
│   ├── table.py              # Table rendering
│   ├── summary_render.py     # Summary display
│   ├── sharp_box.py          # Box drawing utilities
│   └── decorators.py         # Message decorators
│
├── utils/                    # Utility functions
│   ├── file_manager.py       # File operations
│   └── utility.py            # General utilities
│
├── data/                     # Data directory
│   ├── COMBO.TXT             # Generated combo file
│   ├── SSH-GOODS.TXT         # Successful connections
│   ├── SSH-DETAILES.TXT      # Detailed connection info
│   ├── HONEYPOTS.TXT         # Detected honeypots
│   └── debug.log             # Debug logs
│

```

---

## 🔍 Advanced Features

### Honeypot Detection

ChSSHKracker includes a sophisticated multi-layer honeypot detection system that analyzes:

- **Command Output Analysis**: Detects suspicious patterns in command responses
- **Response Time Analysis**: Identifies unnaturally fast response times
- **File System Analysis**: Checks for minimal or fake file systems
- **Process Analysis**: Detects known honeypot processes (Cowrie, Kippo, etc.)
- **Network Analysis**: Examines network configuration for anomalies
- **Behavioral Tests**: Tests system behavior and permissions
- **Performance Tests**: Analyzes system performance characteristics
- **Anomaly Detection**: Identifies suspicious hostnames and system information

Honeypots are automatically logged to `data/HONEYPOTS.TXT` and excluded from successful results.

### System Reconnaissance

Upon successful connection, the tool automatically gathers:

- System hostname and OS information
- Kernel version
- Uptime
- Network configuration
- Running processes
- File system structure
- User information

All reconnaissance data is saved to `data/SSH-DETAILES.TXT`.

### Real-Time Statistics

The tool provides real-time statistics including:

- Total tasks completed
- Successful connections
- Failed attempts
- Honeypots detected
- Current speed (attempts per second)
- Estimated time remaining
- Success rate percentage

---

## 📊 Output Files

All output files are saved in the `data/` directory:

| File               | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `SSH-GOODS.TXT`    | Successful SSH connections (IP:PORT:USERNAME:PASSWORD) |
| `SSH-DETAILES.TXT` | Detailed information about successful connections      |
| `HONEYPOTS.TXT`    | Detected honeypot systems                              |
| `COMBO.TXT`        | Generated combo file (if not provided)                 |
| `debug.log`        | Debug logging information                              |

### Output Format Example

**SSH-GOODS.TXT:**

```
192.168.1.1:22:root:password123
192.168.1.5:22:admin:admin
```

---

## ⚠️ Disclaimer

**This tool is for educational and authorized security testing purposes only.**

- ⚠️ **Unauthorized access to computer systems is illegal**
- ⚠️ **Only use this tool on systems you own or have explicit written permission to test**
- ⚠️ **The authors are not responsible for any misuse of this software**
- ⚠️ **Use responsibly and in compliance with applicable laws**

**By using this tool, you agree to use it only for legitimate security testing and educational purposes.**

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```
Copyright 2025 Ch4120N

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## 👤 Programmer

**Ch4120N**

- GitHub: [@Ch4120N](https://github.com/Ch4120N)
- Project: [ChSSHKracker](https://github.com/Ch4120N/ChSSHKracker)

---

<div align="center">

### ⭐ If you find this project useful, please consider giving it a star! ⭐

**Made with ❤️ by Ch4120N**

---

[![GitHub stars](https://img.shields.io/github/stars/Ch4120N/ChSSHKracker.svg?style=social&label=Star)](https://github.com/Ch4120N/ChSSHKracker)
[![GitHub forks](https://img.shields.io/github/forks/Ch4120N/ChSSHKracker.svg?style=social&label=Fork)](https://github.com/Ch4120N/ChSSHKracker)

</div>
