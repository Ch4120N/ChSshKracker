import sys
from colorama import Fore as Kolor, init
init()

def Logo():
    return fr"""{Kolor.YELLOW}
_________ .__      _________      .__     ____  __.                     __                 
\_   ___ \|  |__  /   _____/ _____|  |__ |    |/ _|___________    ____ |  | __ ___________ 
/    \  \/|  |  \ \_____  \ /  ___/  |  \|      < \_  __ \__  \ _/ ___\|  |/ // __ \_  __ \
\     \___|   Y  \/        \\___ \|   Y  \    |  \ |  | \// __ \\  \___|    <\  ___/|  | \/
 \______  /___|  /_______  /____  >___|  /____|__ \|__|  (____  /\___  >__|_ \\___  >__|   {Kolor.RED}Powered By Ch4120N{Kolor.YELLOW}
        \/     \/        \/     \/     \/        \/           \/     \/     \/    \/          {Kolor.CYAN}Version 1.0{Kolor.RESET}
    """



def Usage():
    return Logo()+"""
Usage: %s -i [TARGET IP OR/IP LIST] [OPTIONS]

Options:
  -h, --help                 show this help message and exit
  -v, --version              show version of script and exit
  -i, --target-ip IP/FILE    target ip or/ targets ip file (e.g: IP:PORT) for attack
  -p, --target-port PORT     target port for attack (Default: 22)
  -C, --combolist            combolist file for attack
  -U, --username             target username or/ username list file for attack
  -P, --password             target password or/ password list file for attack
  -d, --dictionary-attack    set cracking method to dictionary attack (Default)
  -b, --bruteforce-attack    set cracking method to bruteforce attack
  -l, --bruteforce-length    length of bruteforce strings (Default: 8)
  -t, --threads              amount of threads (Default: 10)
  -T, --timeout              timeout of connections (Default: 2)
  -O, --output               output file name
  -V, --verbose              real-time showing results
    """ % (sys.argv[0])