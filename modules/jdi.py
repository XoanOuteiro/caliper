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
Handle logic for binary search of minimum ammount of
Junk Data Injection needed to bypass a WAF
'''
class JDIHandler:

    '''
    --- Instance Attributes ---
    '''
    request_item = None # ReqHandler instance that contains the user-provided request data (post-parsed)
    min_size = None # The minimum amount of junk data to be used
    max_size = None # The maximum amount of data to be used
    segment = None 
    code = None
    match_content = None
    
    '''
    --- Constructors ---
    '''
    def __init__(self,request_item,min_size,max_size,segment,code,match_content):
        self.request_item = request_item
        self.segment = segment
        self.code = code
        self.match_content = match_content

        if min_size >= max_size:
            Utilities.print_error_msg("MIN_SIZE cannot be >= MAX_SIZE")
        else:
            self.min_size = min_size
            self.max_size = max_size
        Utilities.print_success_msg("JDI module instanced, starting...")
        
        self.perform_test()
        self.perform_jdi_search()


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
                Utilities.print_error_msg(f"Response code didnt match on exploratory request. Code was {actual_code}")
                if self.match_content:
                    self._check_content(response.text)

        except Exception as e:
            Utilities.print_error_msg(f"Request failed: {str(e)}")

    def perform_jdi_search(self):
        """
        Performs a binary search to find the minimum amount of junk data needed
        to bypass the WAF. Uses the binary search algorithm to efficiently find
        the smallest payload size that causes a bypass.
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

        # Define search boundaries
        min_bytes = self.min_size
        max_bytes = self.max_size
        best_size = None

        # Test minimum size first to potentially skip binary search
        junk = self._generate_junk(min_bytes)
        modified_body = self._prepare_body_with_junk(junk)
        
        try:
            response = requests.post(
                url=self.request_item.full_url,
                headers=self.request_item.headers,
                data=modified_body,
                verify=False
            )
            
            status = response.status_code
            Utilities.print_success_msg(f"Sent {min_bytes}B")
            
            # If minimum size works, we're done
            if status != self.code:
                Utilities.print_result_msg(f"Potential WAF bypass: Status code: {status} for {min_bytes}B")
                Utilities.print_result_msg(f"Minimum size already works!")
                best_size = min_bytes
            else:
                # Binary search
                low = min_bytes
                high = max_bytes
                
                # We've already tested min_bytes, so start from the next possible size
                tested_sizes = {min_bytes}
                
                while low < high:
                    # Calculate middle point
                    mid = low + (high - low) // 2
                    
                    # If this is the same as the previous size, we need to increment
                    if mid in tested_sizes:
                        # If we can't increment further, we're done
                        if mid + 1 > high:
                            break
                        mid += 1
                    
                    tested_sizes.add(mid)
                    
                    junk = self._generate_junk(mid)
                    modified_body = self._prepare_body_with_junk(junk)
                    
                    try:
                        response = requests.post(
                            url=self.request_item.full_url,
                            headers=self.request_item.headers,
                            data=modified_body,
                            verify=False
                        )
                        
                        status = response.status_code
                        Utilities.print_success_msg(f"Sent {mid}B")
                        
                        bypassed = (status != self.code)
                        
                        if bypassed:
                            Utilities.print_result_msg(f"Potential WAF bypass: Status code: {status} for {mid}B")
                            best_size = mid
                            high = mid - 1  # Look for smaller successful sizes
                        else:
                            low = mid + 1  # Look for larger sizes
                    
                    except Exception as e:
                        Utilities.print_error_msg(f"Request failed: {str(e)}")
                        low = mid + 1  # Move on after an error
        
        except Exception as e:
            Utilities.print_error_msg(f"Initial request failed: {str(e)}")
        
        # Final result
        if best_size:
            Utilities.print_result_msg(f"Smallest successful junk size: {best_size}B")
        else:
            Utilities.print_error_msg("No successful bypass found in the specified range")

    def _generate_junk(self, size_in_bytes):
        """
        Generate random junk data of a specified size in bytes.
        
        Args:
            size_in_bytes (int): Target size of junk data in bytes
            
        Returns:
            str: Random junk data string with approximate size of size_in_bytes
        """
        # Characters in ASCII typically use 1 byte in UTF-8, but some special chars might use more
        # Using a 0.75 factor to account for potential overhead and ensure we don't generate too much data
        estimated_chars = int(size_in_bytes * 0.75)
        
        # Generate basic ASCII characters for consistent byte size
        charset = string.ascii_letters + string.digits
        junk = ''.join(random.choices(charset, k=estimated_chars))
        
        # Calculate actual size and adjust if needed
        actual_bytes = len(junk.encode('utf-8'))
        
        # If we're under target size, add more characters
        if actual_bytes < size_in_bytes:
            additional_chars = int((size_in_bytes - actual_bytes) * 0.75)
            junk += ''.join(random.choices(charset, k=additional_chars))
        
        # If we're over target size, trim the string
        actual_bytes = len(junk.encode('utf-8'))
        if actual_bytes > size_in_bytes:
            # Calculate how many characters to remove to reach target size
            # This is an approximation that might need multiple iterations for perfect accuracy
            excess_bytes = actual_bytes - size_in_bytes
            chars_to_remove = int(excess_bytes * 0.75)
            junk = junk[:-chars_to_remove]
        
        return junk

    def _prepare_body_with_junk(self, junk_data):
        """
        Prepare the request body by adding junk data in an appropriate format 
        that doesn't break the request structure.
        
        For form-urlencoded requests, adds junk as an additional parameter
        rather than as a comment to avoid breaking the request syntax.
        
        Args:
            junk_data (str): Random junk data to add to the request
            
        Returns:
            str: Modified request body with junk data added
        """
        # Determine the content type
        content_type = self.request_item.headers.get('Content-Type', '').lower()
        
        if 'application/x-www-form-urlencoded' in content_type:
            # For form data, add junk as an additional parameter instead of a comment
            # Parse original body to see if it has parameters
            original_body = self.request_item.body.replace('FUZZ', self.segment)
            
            # Add junk as a new parameter, ensuring it doesn't break the request structure
            if '=' in original_body:
                # Body already has parameters, add another one
                return f"{original_body}&junk_data={junk_data}"
            else:
                # No parameters yet, add as first parameter
                return f"junk_data={junk_data}&{original_body}"
        
        elif 'application/json' in content_type:
            # For JSON, use a proper JSON comment that won't break the structure
            if original_body.strip().startswith('{'):
                # It's a JSON object, add a junk property
                modified_body = original_body.replace('FUZZ', self.segment)
                # Remove the closing bracket to add our property
                if modified_body.strip().endswith('}'):
                    modified_body = modified_body.rstrip().rstrip('}')
                    return f"{modified_body}, \"junk_data\": \"{junk_data}\""
                else:
                    return f"{modified_body}, \"junk_data\": \"{junk_data}\""
            else:
                # If it's not a proper JSON structure, fall back to appending
                return f"{self.request_item.body.replace('FUZZ', self.segment)}&junk_data={junk_data}"
        
        elif 'text/html' in content_type:
            # For HTML, add junk as a hidden input field
            modified_body = self.request_item.body.replace('FUZZ', self.segment)
            return f"{modified_body}<input type='hidden' name='junk_data' value='{junk_data}'>"
        
        else:
            # For other content types, try adding as a parameter
            modified_body = self.request_item.body.replace('FUZZ', self.segment)
            
            # Check if we should add as a parameter
            if '=' in modified_body:
                return f"{modified_body}&junk_data={junk_data}"
            else:
                # Best effort to add junk without breaking syntax
                return f"{modified_body}&junk_data={junk_data}"
