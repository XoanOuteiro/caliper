'''
-- Caliper
-- author/s: @XoanOuteiro
'''

import requests
from utils.utilities import Utilities
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

'''
Conducts the EVAL mode to discover potentially useful
non-blocked content
'''
class Evaluator:
    '''
    --- Instance Attributes ---
    '''
    url: str = None
    parameter: str = None
    syntax : str = None

    '''
    --- Constructors ---
    '''
    def __init__(self, url: str, parameter: str, syntax : str):

        if self.validate_url_parameter(url, parameter):
            Utilities.print_success_msg(f"Successfuly parsed {parameter} for {url}")
            self.url = url
            self.parameter = parameter
            self.syntax = syntax
        else:
            Utilities.print_error_msg(f"Couldnt parse {parameter} on {url}")

    '''
    --- Instance Methods ---
    '''
    def validate_url_parameter(self, url, parameter):
        # Check if URL is not None
        if url is None:
            return False

        # Parse the URL to extract query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Check if the parameter exists in the query string
        if parameter in query_params:
            return True
        return False


    def evaluate_wordlist(self, wordlist_path: str):
        """
        This method accepts a wordlist file with one item per line, sends requests
        to the URL with each word as a parameter, and groups them by their response codes.
        
        :param wordlist_path: Path to the wordlist file.
        :return: None
        """
        # Dictionary to store response codes and the corresponding words
        response_groups = defaultdict(list)

        try:
            # Open the wordlist file and read the words
            with open(wordlist_path, 'r') as file:
                words = file.readlines()

            # Loop through each word in the wordlist
            for word in words:
                word = word.strip()  # Remove any extra whitespace or newline characters
                if word:  # Skip empty lines
                    response_code = self.send_request(word)
                    if response_code is not None:  # Only group valid responses
                        response_groups[response_code].append(word)
            
            # Print the results
            for code, words in response_groups.items():
                print(f"Response Code {code}:")
                for word in words:
                    print(f"  - {word}")
        
        except FileNotFoundError:
            Utilities.print_error_msg(f"File not found: {wordlist_path}")
        except Exception as e:
            Utilities.print_error_msg(f"An error occurred: {e}")


    def send_request(self, word: str):
        """
        Sends an HTTP GET request with the word as a query parameter and returns the response code.
        
        :param word: Word to send as a parameter.
        :return: HTTP response code or None if the request fails.
        """
        try:
            # Create the full URL with the parameter
            full_url = f"{self.url}?{self.parameter}={word}"
            response = requests.get(full_url)
            return response.status_code
        except requests.RequestException as e:
            # Log the warning and return None
            Utilities.print_warning_msg(f"Request failed for word {word}: {e}")
            return None  # If the request fails, return None