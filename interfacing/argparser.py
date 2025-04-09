import argparse

from modules.evaluator import Evaluator
from modules.jdi import JDIHandler

from utils.utilities import Utilities
from utils.reqhandler import ReqHandler

'''
Build and collect CLI arguments
(Masquarade for argparse)
'''
class Argparser:
    description_text = "CALIPER - WAF Bypass tool"
    epilog_text = "Thanks for running!"

    mode_options = ["VEC", "EVAL"]
    vector_options = ["JDI", "OHT", "HVS", "RPC"]
    eval_options = ["HTML", "SQL", "LFI"]

    parser = None  # For argparse instance, is assigned at constructor

    def __init__(self):
        self.build()


    def parse_vector(self, args, request_item):
        match args.Vector:
            case "JDI":
                self.instance_JDI(args, request_item)
            case "OHT":
                self.instance_OHT(args, request_item)
            case "HVS":
                self.instance_HVS(args, request_item)
            case "RPC":
                self.instance_RPC(args, request_item)

    def instance_JDI(self, args, request_item):
        if not args.min_size or not args.max_size:
            Utilities.print_error_msg("MIN_SIZE/MAX_SIZE need to be set")
        else:
            try:
                JDIHandler(request_item, int(args.min_size), int(args.max_size), str(args.segment),int(args.code),bool(args.match_content))
            except Exception as error:
                Utilities.print_error_msg("MIN_SIZE/MAX_SIZE are not numerical values",print(error))

    def instance_OHT(self, args, request_item):
        Utilities.print_error_msg("Not yet implemented")

    def instance_HVS(self, args, request_item):
        Utilities.print_error_msg("Not yet implemented")

    def instance_RPC(self, args, request_item):
        Utilities.print_error_msg("Not yet implemented")

    '''
    Check if CLI options are valid
    '''
    def parse_options(self, args):
        # VEC MODE CHECKS
        if args.Mode == "VEC":
            # Check Vector is set
            if not args.Vector:
                Utilities.print_error_msg("Vector is required on VEC mode")
            else:
                Utilities.print_success_msg(f"Caliper will instance {args.Vector} module")

            if not args.protocol:
                Utilities.print_error_msg("No HTTP/HTTPS protocol specified")

            if not args.segment:
                Utilities.print_error_msg("Segment is required on VEC mode")
            else:
                Utilities.print_success_msg(f"Set segment: {args.segment}")

            if not args.code:
                Utilities.print_error_msg("Code is required on VEC mode")
            else:
                Utilities.print_success_msg(f"Exploratory check will need to match response code: {args.code}")

            if args.match_content:
                Utilities.print_success_msg(f"Content matching is ON")
            else:
                Utilities.print_success_msg(f"Content matching is OFF")

            if not args.request_file:
                Utilities.print_error_msg("Request File is required on VEC mode")
            else:
                serialized_req = ReqHandler(args.request_file, args.protocol)

            # ALl general checks OK, begin module loading
            self.parse_vector(args, serialized_req)


        # EVAL MODE CHECKS
        elif args.Mode == "EVAL":

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

        # Create a subparser for Mode to distinguish VEC and EVAL modes
        subparsers = self.parser.add_subparsers(dest="Mode")

        # VEC Mode subparser
        vec_parser = subparsers.add_parser('VEC', help="Vectorization mode options")
        vec_parser.add_argument("Vector", type=str, help=f"For VEC mode, The evasion vector to attempt: {str(self.vector_options)}", choices=self.vector_options)

        vec_parser.add_argument("-p","--protocol", type=str, help="The HTTP protocol type to use, can be HTTP or HTTPS", choices=["http","https"])
        vec_parser.add_argument("-s", "--segment", type=str, help="The string which caused WAF blockage (which you should have replaced by FUZZ in the request file)")
        vec_parser.add_argument("-rf", "--request-file", type=str, help="The file containing the POST-like request to use, must have the term FUZZ in the area that you want the vectorized segment to be. You can obtain a plain TXT request via tools like Burp Suite or Caido")
        vec_parser.add_argument("-c", "--code", type=str, help="The HTTP Response code that was given when being blocked by WAF (If its 200-like make sure to turn on content-matching)")

        vec_parser.add_argument("-mc", "--match-content", action="store_true", help="Shows a success message if the content of the webpage changed between the initial test connection (done with the base segment) and a vectorized segment connection."
        " Useful for when the WAF gives a 200 response code on blockage. (You will also receive a typical code-changed success message)")

        # POST-Based and POST-like Arguments
        vec_parser.add_argument("--min-size", type=str, help="The minimum amount of Junk data to be used by JDI (in kilobytes)")
        vec_parser.add_argument("--max-size", type=str, help="The maximum amount of Junk data to be used by JDI (in kilobytes)")

        # EVAL Mode subparser
        eval_parser = subparsers.add_parser('EVAL', help="Evaluation mode options")
        eval_parser.add_argument("-u", "--url", type=str, help="Target URL to evaluate (e.g., http://site.net/search?query=hello)")
        eval_parser.add_argument("-p", "--parameter", type=str, help="GET Parameter to target, make sure dataspace begins with = and ends blank or with &")
        eval_parser.add_argument("-st", "--syntax-type", type=str, help=f"Syntax type to test on EVAL mode: {str(self.eval_options)}", choices=self.eval_options)

        args = self.parser.parse_args()
        self.parse_options(args)

