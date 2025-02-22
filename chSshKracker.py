import sys, time
import argparse
from Core.banner import Logo, Usage
from Core.utils import MessageLog as msglog

class CustomHelpFormatter(argparse.HelpFormatter):
    """A custom HelpFormatter class that capitalizes the first letter of usage text."""
    def add_usage(self, usage, actions, groups, prefix=None):
        """Add usage method to display the usage text with the first letter capitalized."""
        if prefix is None:
            prefix = ''
        return super(CustomHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)



class chSshKracker:
    def __init__(self):
        self.version = "ChSshKracker v1.0"
    def programStartup(self):
        parser = argparse.ArgumentParser(formatter_class=CustomHelpFormatter, add_help=False)

        parser.add_argument_group("Options")
        parser.add_argument('-v', '--version', dest='programVersion', help='show version and exit', action='store_true', default=False)
        parser.add_argument('-i', '--target-ip', dest='targetIP', help='target ip or/ targets ip file (e.g: IP:PORT) for attack')
        parser.add_argument('-p', '--target-port', dest='targetPort', help='target port for attack')
        parser.add_argument('-c', '--combolist', dest='combolistFile', help='combolist file for attack')
        parser.add_argument('-U', '--username', dest='targetUsername', help='target username or/ username list file for attack')
        parser.add_argument('-P', '--password', dest='targetPassword', help='target password or/ password list file for attack')
        parser.add_argument('-d', '--dictionary-attack', dest='dictionaryMethod', action='store_true', help='set cracking method to dictionary attack', default=True)
        parser.add_argument('-b', '--bruteforce-attack', dest='bruteforceMethod', action='store_true', help='set cracking method to bruteforce attack')
        parser.add_argument('-l', '--bruteforce-length', dest='bruteforceLength', type=int, help='length of bruteforce strings (Default: 8)', default=8)
        parser.add_argument('-t', '--threads', dest='amountThreads', type=int, help='length of bruteforce strings (Default: 10)', default=10)
        parser.add_argument('-T', '--timeout', dest='connectionTimeout', type=int, help='timeout of connections (Default: 2)', default=2)
        parser.add_argument('-O', '--output', dest='outputFile', help='output file name')
        parser.add_argument('-V', '--verbose', action='store_true', help='real-time showing results', default=False)

        parser.error = lambda message: print(Usage()) or sys.exit(2)
        args = parser.parse_args()

        if (not args.targetIP):
            if args.programVersion:
                msglog.success(self.version)
                sys.exit(0)
            print(Usage())
            sys.exit(2)

        if (args.dictionaryMethod):
            if (not args.targetUsername):
                msglog.error("For the dictionary attack method you need a username list or a single username")
            elif (not args.targetPassword):
                msglog.error("For the dictionary attack method you need a password list or a single password")
            
if  __name__ == '__main__':
    app = chSshKracker()
    sys.exit(app.programStartup())