'''
-- Caliper
-- module: Origin Header Tampering (OHT)
-- author/s: @XoanOuteiro
'''

from utils.reqhandler import ReqHandler
from utils.utilities import Utilities
import requests
import itertools

'''
Handle logic for Origin Header Tampering to bypass WAF protections
by making the WAF believe the request is coming from a trusted source.
'''
class OHTHandler:

    '''
    --- Instance Attributes ---
    '''
    request_item = None  # ReqHandler instance that contains the user-provided request data
    segment = None       # The segment that causes WAF blockage
    code = None          # The HTTP response code that indicates WAF blockage
    match_content = None # Flag to enable content matching for 200-like responses
    origin_headers = [   # List of headers that can be used for origin spoofing
        'X-Originating-IP',
        'X-Forwarded-For',
        'X-Remote-IP',
        'X-Remote-Addr',
        'X-Client-IP',
        'X-Real-IP',
        'X-Forwarded-Host',
        'X-Host',
        'True-Client-IP',
        'Forwarded'
    ]
    trusted_ips = [      # List of potentially trusted IP addresses
        '127.0.0.1',
        '0.0.0.0',
        'localhost',
        '::1',
        '192.168.0.1',
        '10.0.0.1',
        '172.16.0.1'
    ]
    baseline_content = None  # Stores the baseline content for comparison
    
    '''
    --- Constructors ---
    '''
    def __init__(self, request_item, segment, code, match_content):
        self.request_item = request_item
        self.segment = segment
        self.code = int(code)
        self.match_content = match_content
        
        Utilities.print_success_msg("OHT module instanced, starting...")
        
        # Perform initial test to get baseline response
        self.perform_test()
        
        # Perform OHT testing
        self.perform_oht_search()

    '''
    --- Instance Methods ---
    '''
    def perform_test(self):
        """
        Exploratory request to see if the response code matches user given code and establish baseline
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

            Utilities.print_success_msg(f"Sent baseline request with injected segment: {self.segment}")
            actual_code = response.status_code

            if actual_code == self.code:
                Utilities.print_success_msg(f"Response matched WAF block code: {actual_code}, beginning exploration.")
                # Store baseline content for content matching if enabled
                if self.match_content:
                    self.baseline_content = response.text
            else:
                Utilities.print_error_msg(f"Response code didn't match on exploratory request. Code was {actual_code}")
                return

        except Exception as e:
            Utilities.print_error_msg(f"Request failed: {str(e)}")
    
    def perform_oht_search(self):
        """
        Test different origin header combinations to find ones that bypass the WAF
        """
        Utilities.print_success_msg("Starting OHT testing with various header combinations...")
        
        # Track successful bypasses
        successful_bypasses = []
        
        # Test single headers first
        for header, ip in itertools.product(self.origin_headers, self.trusted_ips):
            result = self._test_header_combination({header: ip})
            if result:
                successful_bypasses.append((header, ip))
        
        # If no success with single headers, try combinations of two
        if not successful_bypasses:
            Utilities.print_success_msg("Testing combinations of two headers...")
            for header1, ip1 in itertools.product(self.origin_headers[:5], self.trusted_ips[:4]):
                for header2, ip2 in itertools.product(self.origin_headers[:5], self.trusted_ips[:4]):
                    if header1 != header2:  # Avoid duplicate headers
                        result = self._test_header_combination({header1: ip1, header2: ip2})
                        if result:
                            successful_bypasses.append(((header1, ip1), (header2, ip2)))
        
        # Report results
        if successful_bypasses:
            Utilities.print_result_msg(f"Found {len(successful_bypasses)} successful bypass combinations:")
            for bypass in successful_bypasses:
                if isinstance(bypass[0], tuple):  # This is a combination of headers
                    Utilities.print_result_msg(f"  Header Combination: {bypass[0][0]}: {bypass[0][1]}, {bypass[1][0]}: {bypass[1][1]}")
                else:
                    Utilities.print_result_msg(f"  Header: {bypass[0]}: {bypass[1]}")
        else:
            Utilities.print_error_msg("No successful bypasses found with the tested header combinations.")
    
    def _test_header_combination(self, headers_dict):
        """
        Test a specific combination of origin headers
        
        Args:
            headers_dict (dict): Dictionary of headers to inject
            
        Returns:
            bool: True if bypass was successful, False otherwise
        """
        # Create a copy of the original headers and update with new headers
        modified_headers = self.request_item.headers.copy()
        for header, value in headers_dict.items():
            modified_headers[header] = value
        
        # Replace FUZZ with the segment
        modified_body = self.request_item.body.replace("FUZZ", self.segment)
        
        # Create a header string for display
        headers_str = ", ".join([f"{h}: {v}" for h, v in headers_dict.items()])
        Utilities.print_success_msg(f"Testing headers: {headers_str}")
        
        try:
            response = requests.post(
                url=self.request_item.full_url,
                headers=modified_headers,
                data=modified_body,
                verify=False,
                timeout=10  # Add timeout to prevent hanging
            )
            
            status = response.status_code
            
            # Check if we bypassed based on status code
            bypassed = (status != self.code)
            
            # If status code indicates bypass or we need to check content
            if bypassed:
                Utilities.print_result_msg(f"Potential WAF bypass found! Status code: {status} with headers: {headers_str}")
                return True
            elif self.match_content and self.baseline_content:
                # Check if content changed significantly from baseline
                if self._check_content_changed(response.text):
                    Utilities.print_result_msg(f"Potential WAF bypass found! Content changed with headers: {headers_str}")
                    return True
            
            return bypassed
            
        except Exception as e:
            Utilities.print_error_msg(f"Request failed: {str(e)}")
            return False
    
    def _check_content_changed(self, current_content):
        """
        Check if the response content has changed significantly from baseline
        
        Args:
            current_content (str): Current response content
            
        Returns:
            bool: True if content appears to have changed significantly, False otherwise
        """
        if not self.baseline_content:
            return False
            
        # Simple length check as a first indicator
        length_diff = abs(len(current_content) - len(self.baseline_content))
        length_change_percent = (length_diff / len(self.baseline_content)) * 100
        
        # If length changed significantly, consider it a change
        if length_change_percent > 10:  # 10% threshold for length change
            return True
            
        # Further checks could be implemented here, such as:
        # - Check for absence of common WAF block indicators
        # - Check for presence of expected content in non-blocked responses
        # - Compare response structure or key elements
        
        return False
