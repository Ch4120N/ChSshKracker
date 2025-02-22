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
  -i, --target-ip IP/FILE    target ip or/ targets ip file (e.g: IP:PORT) for attack
  -p, --target-port PORT     target port for attack
  -d, --dictionary-attack    set cracking method to dictionary attack
  -b, --bruteforce-attack    set cracking method to bruteforce attack

    """ % (sys.argv[0])