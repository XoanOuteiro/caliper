'''
-- Caliper
-- author/s: @XoanOuteiro
'''

import random
import sys

'''
Miscellaneus utilities such as version,
logo, ascii art etc.
'''
class Utilities:

    '''
    --- Instance Attributes ---
    '''
    VERSION = "pre-alpha 0.0.1"

    logo=""" ________  ________  ___       ___  ________  _______   ________     
|\   ____\|\   __  \|\  \     |\  \|\   __  \|\  ___ \ |\   __  \    
\ \  \___|\ \  \|\  \ \  \    \ \  \ \  \|\  \ \   __/|\ \  \|\  \   
 \ \  \    \ \   __  \ \  \    \ \  \ \   ____\ \  \_|/_\ \   _  _\  
  \ \  \____\ \  \ \  \ \  \____\ \  \ \  \___|\ \  \_|\ \ \  \\  \| 
   \ \_______\ \__\ \__\ \_______\ \__\ \__\    \ \_______\ \__\\ _\ 
    \|_______|\|__|\|__|\|_______|\|__|\|__|     \|_______|\|__|\|__|
                                                                     
                                                                     
                                                                     """

    '''
    --- Constructors ---
    '''

    '''
    --- Instance Methods ---
    '''
    def get_random_quote():
        try:
            # Open the file and read all lines
            with open('./wordlists/quotes.txt', 'r') as file:
                quotes = file.readlines()
            
            # Remove any leading/trailing whitespace characters from each quote
            quotes = [quote.strip() for quote in quotes]
            
            # Return a random quote from the list
            return random.choice(quotes)
        
        except FileNotFoundError:
            return "[UTILS] -> The file 'quotes.txt' was not found."
        except Exception as e:
            return str(e)
        
        
    def print_separator(char='-', length=40):
        print(char * length)


    def print_success_msg(message: str):
        # ANSI escape codes for green and gray
        GREEN = "\033[32m"
        GRAY = "\033[90m"
        RESET = "\033[0m"
        
        print(f"{GREEN}[+] OK -> {RESET}{message}{RESET}")


    def print_warning_msg(message: str):
        # ANSI escape codes for yellow and gray
        YELLOW = "\033[33m"
        GRAY = "\033[90m"
        RESET = "\033[0m"
        
        print(f"{YELLOW}[!] WARNING -> {RESET}{message}{RESET}")


    def print_error_msg(message: str):
        # ANSI escape codes for red and gray
        RED = "\033[31m"
        GRAY = "\033[90m"
        RESET = "\033[0m"
        
        print(f"{RED}[x] ERROR -> {RESET}{message}{RESET}")
        sys.exit()
    