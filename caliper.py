'''
-- Caliper
-- author/s: @XoanOuteiro
'''

from interfacing.argparser import Argparser
from utils.utilities import Utilities

def run():
    args = Argparser()

if __name__ == "__main__":

    Utilities.print_separator("<>", 30)
    print(Utilities.logo + "\n\t --- " + Utilities.VERSION + " --- by @XoanOuteiro")
    print(Utilities.get_random_quote())
    Utilities.print_separator("<>", 30)

    run()