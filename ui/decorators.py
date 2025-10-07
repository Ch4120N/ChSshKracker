# -*- UTF-8 -*-
# ui/decorators.py

from colorama import Fore, Style, init

init(autoreset=True)


class StatusDecorator:
    def __init__(self):
        self.PASS = Style.BRIGHT + Fore.GREEN + \
            "\n [ " + Style.BRIGHT + Fore.WHITE + "+" + \
            Style.BRIGHT + Fore.GREEN + " ] " + Style.RESET_ALL
        self.FAIL = Style.BRIGHT + Fore.RED + \
            "\n [ " + Style.BRIGHT + Fore.WHITE + "-" + \
            Style.BRIGHT + Fore.RED + " ] " + Style.RESET_ALL
        self.WARN = Style.BRIGHT + Fore.YELLOW + \
            "\n [ " + Style.BRIGHT + Fore.WHITE + "!" + \
            Style.BRIGHT + Fore.YELLOW + " ] " + Style.RESET_ALL
        self.HEAD = Style.BRIGHT + Fore.CYAN + \
            "\n [ " + Style.BRIGHT + Fore.WHITE + "::" + \
            Style.BRIGHT + Fore.CYAN + " ] " + Style.RESET_ALL
        self.INFO = Style.BRIGHT + Fore.CYAN + \
            "\n [ " + Style.BRIGHT + Fore.WHITE + "*" + \
            Style.BRIGHT + Fore.CYAN + " ] " + Style.RESET_ALL
        self.STDS = "           "

class MessageDecorator(StatusDecorator):
    def InfoMessage(self, RequestMessage):
        print(self.INFO + Style.RESET_ALL + RequestMessage)
    
    def SuccessMessage(self, RequestMessage):
        print(self.PASS + Style.RESET_ALL + RequestMessage)

    def FailureMessage(self, RequestMessage):
        print(self.FAIL + Style.RESET_ALL + RequestMessage)

    def WarningMessage(self, RequestMessage):
        print(self.WARN + Style.RESET_ALL + RequestMessage)

    def SectionMessage(self, RequestMessage):
        print(self.HEAD + Fore.CYAN + Style.BRIGHT
              + RequestMessage + Style.RESET_ALL)

    def GeneralMessage(self, RequestMessage):
        print(self.STDS + Style.RESET_ALL + RequestMessage)