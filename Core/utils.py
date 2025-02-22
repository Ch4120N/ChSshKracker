import os
from colorama import Fore as Kolor, init
init()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

class MessageLog:
    @staticmethod
    def success(message:str):
        print(f" {Kolor.LIGHTGREEN_EX}[{Kolor.WHITE}+{Kolor.LIGHTGREEN_EX}] {message}")
    @staticmethod
    def error(message:str):
        print(f" {Kolor.LIGHTRED_EX}[{Kolor.WHITE}-{Kolor.LIGHTRED_EX}] {message}")
