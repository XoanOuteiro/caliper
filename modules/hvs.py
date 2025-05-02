'''
-- Caliper
-- module: HTTP Verb Swap (HVS)
-- author/s: @XoanOuteiro
'''

from utils.reqhandler import ReqHandler
from utils.utilities import Utilities
import requests

'''
Handle logic for HTTP Verb Swap to bypass WAF protections
by using alternative HTTP methods that may not be evaluated 
or are evaluated differently by the WAF
'''
class HVSHandler:

    '''
    --- Instance Attributes ---
    '''
    request_item = None  # ReqHandler instance that contains the user-provided request data
    segment = None       # The segment that causes WAF blockage
    code = None          # The HTTP response code that indicates WAF blockage
    match_content = None # Flag to enable content matching for 200-like responses
    http_verbs = [       # List of HTTP methods/verbs to test
        'PUT',
        'PATCH',
        # 'OPTIONS',       # Tends to be enabled, can cause false positives, uncomment at own risk
        'HEAD',
        'DELETE',
        'CONNECT',
        'TRACE',
        'PROPFIND',      # WebDAV
        'MKCOL',         # WebDAV
        'COPY',          # WebDAV
        'MOVE',          # WebDAV
        'SEARCH',        # WebDAV
        'ARBITRARY',     # Custom non-standard verb
        'POST'           # Original method (for reference)
        # 'GET'          # Common alternative, but generally useless
    ]
    baseline_content = None  # Stores the baseline content for comparison
    baseline_headers = None  # Stores the baseline response headers
    
    '''
    --- Constructors ---
    '''
    def __init__(self, request_item, segment, code, match_content):
        self.request_item = request_item
        self.segment = segment
        self.code = int(code)
        self.match_content = match_content

        if self.match_content:
            Utilities.print_warning_msg("Content Matching on HVS WILL cause false positives.")
        
        Utilities.print_success_msg("HVS module instanced, starting...")
        
        # Perform initial test to get baseline response
        self.perform_test()
        
        # Perform HVS testing
        self.perform_hvs_search()

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
                # Store baseline content and headers for comparison if content matching is enabled
                if self.match_content:
                    self.baseline_content = response.text
                    self.baseline_headers = response.headers
            else:
                Utilities.print_error_msg(f"Response code didn't match on exploratory request. Code was {actual_code}")
                return

        except Exception as e:
            Utilities.print_error_msg(f"Request failed: {str(e)}")
    
    def perform_hvs_search(self):
        """
        Test different HTTP verbs to find ones that bypass the WAF
        """
        Utilities.print_success_msg("Starting HVS testing with various HTTP methods...")
        
        # Track successful bypasses
        successful_bypasses = []
        
        # Test each HTTP verb
        for verb in self.http_verbs:
            result = self._test_http_verb(verb)
            if result:
                successful_bypasses.append(verb)
        
        # Report results
        if successful_bypasses:
            Utilities.print_result_msg(f"Found {len(successful_bypasses)} successful bypass verbs:")
            for verb in successful_bypasses:
                Utilities.print_result_msg(f"  HTTP Method: {verb}")
        else:
            Utilities.print_error_msg("No successful bypasses found with the tested HTTP verbs.")
    
    def _test_http_verb(self, verb):
        """
        Test a specific HTTP verb/method
        
        Args:
            verb (str): HTTP method to test
            
        Returns:
            bool: True if bypass was successful, False otherwise
        """
        # Replace FUZZ with the segment
        modified_body = self.request_item.body.replace("FUZZ", self.segment)
        
        Utilities.print_success_msg(f"Testing HTTP method: {verb}")
        
        try:
            # Use requests.request to dynamically set the HTTP method
            response = requests.request(
                method=verb,
                url=self.request_item.full_url,
                headers=self.request_item.headers,
                data=modified_body,
                verify=False,
                timeout=10  # Add timeout to prevent hanging
            )
            
            status = response.status_code
            
            # Check if we bypassed based on status code
            bypassed = (status != self.code and status != 405)
            
            # Log detailed information about the response
            Utilities.print_success_msg(f"Response for {verb}: Status {status}, Content length: {len(response.text)}")
            
            # If status code indicates bypass
            if bypassed:
                Utilities.print_result_msg(f"Potential WAF bypass found! Status code: {status} with HTTP method: {verb}")
                return True
            # If status code doesn't indicate bypass but we need to check content
            elif self.match_content and self.baseline_content:
                # Check if content changed significantly from baseline
                if self._check_content_changed(response.text, response.headers):
                    Utilities.print_result_msg(f"Potential WAF bypass found! Content changed with HTTP method: {verb}")
                    return True
            
            return bypassed
            
        except Exception as e:
            Utilities.print_error_msg(f"Request with {verb} failed: {str(e)}")
            return False
    
    def _check_content_changed(self, current_content, current_headers):
        """
        Check if the response content has changed significantly from baseline
        
        Args:
            current_content (str): Current response content
            current_headers (dict): Current response headers
            
        Returns:
            bool: True if content appears to have changed significantly, False otherwise
        """
        if not self.baseline_content:
            return False
            
        # Simple length check as a first indicator
        length_diff = abs(len(current_content) - len(self.baseline_content))
        length_change_percent = (length_diff / len(self.baseline_content)) * 100 if len(self.baseline_content) > 0 else 100
        
        # Check for WAF signature absence
        # Common WAF block indicators that might be present in blocked responses
        waf_indicators = [
            "blocked",
            "security",
            "violation",
            "firewall",
            "attack",
            "forbidden",
            "unauthorized",
            "denied",
            "access denied"
        ]
        
        # Check if blocked indicators are in baseline but not in current (suggests successful bypass)
        baseline_has_indicator = any(indicator in self.baseline_content.lower() for indicator in waf_indicators)
        current_has_indicator = any(indicator in current_content.lower() for indicator in waf_indicators)
        
        # If baseline shows WAF block but current doesn't, this suggests bypass
        waf_signature_changed = baseline_has_indicator and not current_has_indicator
        
        # Check content type header changes that might indicate bypass
        content_type_changed = False
        if self.baseline_headers and 'Content-Type' in self.baseline_headers:
            baseline_content_type = self.baseline_headers['Content-Type']
            current_content_type = current_headers.get('Content-Type', '')
            content_type_changed = baseline_content_type != current_content_type
        
        # If length changed significantly, consider it a change
        if length_change_percent > 10:  # 10% threshold for length change
            return True
            
        # If WAF signature changed or content type changed, consider it a bypass
        if waf_signature_changed or content_type_changed:
            return True
            
        return False
