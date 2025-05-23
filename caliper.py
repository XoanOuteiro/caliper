'''
-- Caliper
-- author/s: @XoanOuteiro
'''

from interfacing.argparser import Argparser
from utils.utilities import Utilities

def run():
    args = Argparser()

if __name__ == "__main__":

    Utilities.print_separator("=", 60)
    Utilities.print_logo()
    print(Utilities.get_random_quote())
    Utilities.print_separator("=", 60)

    run()
