import sys, time
import argparse
from Core.banner import Logo, Usage


class CustomHelpFormatter(argparse.HelpFormatter):
    """A custom HelpFormatter class that capitalizes the first letter of usage text."""
    def add_usage(self, usage, actions, groups, prefix=None):
        """Add usage method to display the usage text with the first letter capitalized."""
        if prefix is None:
            prefix = ''
        return super(CustomHelpFormatter, self).add_usage(
            usage, actions, groups, prefix)



class chSshKracker:
    def programStartup(self):
        parser = argparse.ArgumentParser(formatter_class=CustomHelpFormatter, add_help=False)

        parser.add_argument_group("Options")
        parser.add_argument('-i', '--target-ip', dest='targetIP', help='target ip or/ targets ip file (e.g: IP:PORT) for attack', required=True)
        parser.add_argument('-p', '--target-port', dest='targetPort', help='target port for attack')
        parser.add_argument('-d', '--dictionary-attack', dest='dictionaryMethod', action='store_true', help='set cracking method to dictionary attack')
        parser.add_argument('-b', '--bruteforce-attack', dest='bruteforceMethod', action='store_true', help='set cracking method to bruteforce attack')

        parser.error = lambda message: print(Usage()) or sys.exit(2)
        args = parser.parse_args()

        print(args)


if  __name__ == '__main__':
    app = chSshKracker()
    sys.exit(app.programStartup())