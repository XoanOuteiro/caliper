import argparse

'''
Build and collect CLI arguments
(Masquarade for argparse)
'''
class Argparser:

    '''
    --- Instance Attributes ---
    '''
    description_text = "CALIPER - WAF Bypass tool"
    epilog_text = "Thanks for running"

    verb_options = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    vector_options = ["JDI", "OHT", "HVS", "RPC"]

    parser = None # For argparse instace, is assigned at constructor

    '''
    --- Constructors ---
    '''
    def __init__(self):
        self.build()

    '''
    --- Instance Methods ---
    '''
    def build(self):
        self.parser = argparse.ArgumentParser(
                                    description=self.description_text,  
                                     epilog=self.epilog_text)

        # Positional arguments: VERB and Vector
        self.parser.add_argument("HTTP Verb", type=str, help=f"HTTP Verb to use: {str(self.verb_options)}", choices=self.verb_options)
        self.parser.add_argument("Vector", type=str, help=f"The evasion vector to attempt: {str(self.vector_options)}", choices=self.vector_options)

        # Mandatory flagged arguments
        self.parser.add_argument("-u", "--url", type=str, help="The endpoint to attack, in case of GET verb you will need to identify target parameter via -p/--parameter.")

        self.parser.add_argument("-s", "--segment", type=str, help="The string which caused WAF blockage")
        self.parser.add_argument("-c", "--code", type=str, help="The HTTP Response code that was given when being blocked by WAF (If its 200-like make sure to turn on content-matching)")

        self.parser.add_argument("-mc", "--match-content", action="store_true", help="Shows a success message if the content of the webpage changed between the initial test connection "
        "(done with the base segment) and a vectorized segment connection."
        " Useful for when the WAF gives a 200 response code on blockage. (You will also recieve a typical code-changed success message)")

        # GET-Based and GET-like (no request body) Arguments
        self.parser.add_argument("-p","--parameter", type=str, help="GET Parameter to target, make sure dataspace begins with = and ends blank or with &")

        # POST-Based and POST-like Arguments

        # ---
        args = self.parser.parse_args()