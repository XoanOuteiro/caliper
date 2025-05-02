'''
-- Caliper
-- author/s: @XoanOuteiro
'''

from utils.reqhandler import ReqHandler
from utils.utilities import Utilities
import requests
import random
import string

'''
Handle logic for testing if different capitalizations of a segment can bypass a WAF
'''
class RPCHandler:

    '''
    --- Instance Attributes ---
    '''
    request_item = None # ReqHandler instance that contains the user-provided request data (post-parsed)
    segment = None
    code = None
    match_content = None

    '''
    --- Constructors ---
    '''
    def __init__(self, request_item, segment, code, match_content):
        self.request_item = request_item
        self.segment = segment
        self.code = code
        self.match_content = match_content

        Utilities.print_success_msg("RPC module instanced, starting...")
        
        self.perform_test()
        self.perform_rpc_search()

    '''
    --- Instance Methods ---
    '''
    def perform_test(self):
        """
        Exploratory request to see if the response code matches user given code
        """
        if "FUZZ" not in self.request_item.body:
            Utilities.print_error_msg("Request body doesn't contain 'FUZZ', can't inject segment.")
            return

        modified_body = self.request_item.body.replace("FUZZ", self.segment)
        
        try:
            response = requests.post(
                url=self.request_item.full_url,
                headers=self.request_item.headers,
                data=modified_body,
                verify=False 
            )

            Utilities.print_success_msg(f"Sent request with injected segment: {self.segment}")
            actual_code = response.status_code

            if actual_code == int(self.code):
                Utilities.print_success_msg(f"Response matched WAF block code: {actual_code}, beginning exploration.")
            else:
                Utilities.print_error_msg(f"Response code didn't match on exploratory request. Code was {actual_code}")
                if self.match_content:
                    self._check_content(response.text)

        except Exception as e:
            Utilities.print_error_msg(f"Request failed: {str(e)}")

    def perform_rpc_search(self):
        """
        Perform tests by injecting different capitalizations of the segment
        and observing if the response code changes or if match-content is triggered
        """
        # Initialize content baseline for content matching if enabled
        baseline_content = None
        if self.match_content:
            try:
                baseline_response = requests.post(
                    url=self.request_item.full_url,
                    headers=self.request_item.headers,
                    data=self.request_item.body.replace("FUZZ", self.segment),
                    verify=False
                )
                baseline_content = baseline_response.text
            except Exception as e:
                Utilities.print_error_msg(f"Failed to get baseline content: {str(e)}")
                return

        # List of capitalizations to test
        capitalizations = self._generate_capitalizations(self.segment)

        for capitalized_segment in capitalizations:
            modified_body = self.request_item.body.replace("FUZZ", capitalized_segment)

            try:
                response = requests.post(
                    url=self.request_item.full_url,
                    headers=self.request_item.headers,
                    data=modified_body,
                    verify=False
                )

                status = response.status_code
                Utilities.print_success_msg(f"Sent request with segment: {capitalized_segment} (status: {status})")

                if status != self.code:
                    Utilities.print_result_msg(f"Potential WAF bypass: Status code: {status} with segment: {capitalized_segment}")
                    if self.match_content:
                        self._check_content(response.text, baseline_content)

            except Exception as e:
                Utilities.print_error_msg(f"Request failed: {str(e)}")

    def _generate_capitalizations(self, segment):
        """
        Generate different capitalizations of the given segment.
        
        Args:
            segment (str): The segment to generate capitalizations for
        
        Returns:
            list: A list of capitalized variants of the segment
        """
        capitalizations = [
            segment.lower(),
            segment.upper(),
            segment.capitalize(),
            segment.swapcase(),
            ''.join(random.choice([c.upper(), c.lower()]) for c in segment)
        ]
        return capitalizations

    def _check_content(self, response_text, baseline_content=None):
        """
        Compare the response content with the baseline to detect changes.
        
        Args:
            response_text (str): The content of the response
            baseline_content (str): The baseline content for comparison (optional)
        """
        if baseline_content:
            if response_text != baseline_content:
                Utilities.print_success_msg("Content change detected!")
            else:
                Utilities.print_error_msg("No content change detected.")
        else:
            Utilities.print_success_msg("No baseline content to compare.")
