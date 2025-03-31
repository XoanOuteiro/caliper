'''
-- Caliper
-- author/s: @XoanOuteiro
'''

import argparse
from modules.evaluator import Evaluator
from utils.utilities import Utilities

'''
Build and collect CLI arguments
(Masquarade for argparse)
'''
class Argparser:
    description_text = "CALIPER - WAF Bypass tool"
    epilog_text = "Thanks for running!"

    mode_options = ["VEC", "EVAL"]
    verb_options = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    vector_options = ["JDI", "OHT", "HVS", "RPC"]
    eval_options = ["HTML","SQL","LFI"]

    parser = None  # For argparse instance, is assigned at constructor

    def __init__(self):
        self.build()

    '''
    Check if CLI options are valid
    '''
    def parse_options(self, args):

        # VEC MODE CHECKS
        if args.Mode == "VEC":

            # Check Verb and Vector are set
            if not args.Verb:
                Utilities.print_error_msg("HTTP Verb is required on VEC mode")
            if not args.Vector:
                Utilities.print_error_msg("Vector is required on VEC mode")

        # EVAL MODE CHECKS
        else:

            # If the Mode is EVAL, make sure other positionals arent set
            if args.Verb:
                Utilities.print_error_msg("Verb is for VEC mode only.")
            if args.Vector:
                Utilities.print_error_msg("Vector selection is a VEC mode only option")

            # Check URL and Parameter are set
            if not args.url:
                Utilities.print_error_msg("You need to set a target URL such as (http://site.net/search?query=hello)")
            if not args.parameter:
                Utilities.print_error_msg("You need to specify a parameter from target URL to test")
            if not args.syntax_type:
                Utilities.print_error_msg(f"You need to set the syntax type to test: {self.eval_options}")
            
            # By now, all should be valid, so launch module.
            Utilities.print_success_msg("EVAL mode parameter syntax correct")
            Evaluator(args.url, args.parameter, args.syntax_type)

    '''
    Builds the CLI interface
    '''
    def build(self):
        self.parser = argparse.ArgumentParser(
            description=self.description_text,  
            epilog=self.epilog_text
        )

        # Positional argument for Mode
        self.parser.add_argument("Mode", type=str, help=f"Caliper mode to use: {str(self.mode_options)}", choices=self.mode_options)

        # HTTP Verb, Vector and EVAL mode will be optional based on Mode
        self.parser.add_argument("Verb", type=str, help=f"For VEC mode, HTTP Verb to use: {str(self.verb_options)}", choices=self.verb_options, nargs='?')
        self.parser.add_argument("Vector", type=str, help=f"For VEC mode, The evasion vector to attempt: {str(self.vector_options)}", choices=self.vector_options, nargs='?')

        # Mandatory flagged arguments
        self.parser.add_argument("-u", "--url", type=str, help="The endpoint to attack, in case of GET verb you will need to identify target parameter via -p/--parameter.")
        self.parser.add_argument("-s", "--segment", type=str, help="The string which caused WAF blockage")
        self.parser.add_argument("-c", "--code", type=str, help="The HTTP Response code that was given when being blocked by WAF (If its 200-like make sure to turn on content-matching)")

        self.parser.add_argument("-mc", "--match-content", action="store_true", help="Shows a success message if the content of the webpage changed between the initial test connection "
        "(done with the base segment) and a vectorized segment connection."
        " Useful for when the WAF gives a 200 response code on blockage. (You will also recieve a typical code-changed success message)")

        # GET-Based and GET-like (no request body) Arguments
        self.parser.add_argument("-p", "--parameter", type=str, help="GET Parameter to target, make sure dataspace begins with = and ends blank or with &")
        self.parser.add_argument("-st","--syntax-type", type=str, help=f"Syntax type to test on EVAL mode: {str(self.eval_options)}", choices=self.eval_options)

        # POST-Based and POST-like Arguments
        self.parser.add_argument("--min-size", type=str, help="The minimun ammount of Junk data to be used by JDI (in kylobytes)")
        self.parser.add_argument("--max-size", type=str, help="The maximun ammount of Junk data to be used by JDI (in kylobytes)")

        args = self.parser.parse_args()

        self.parse_options(args)
