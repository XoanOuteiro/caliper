'''
-- Caliper
-- author/s: @XoanOuteiro
'''

import requests
import time
from utils.utilities import Utilities
from urllib.parse import urlparse, parse_qs, urlencode
from collections import defaultdict
from tqdm import tqdm


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
    syntax: str = None

    '''
    --- Constructors ---
    '''
    def __init__(self, url: str, parameter: str, syntax: str):
        if self.validate_url_parameter(url, parameter):
            Utilities.print_success_msg(f"Successfully parsed {parameter} for {url}")
            self.url = url
            self.parameter = parameter
            self.syntax = syntax
            Utilities.print_warning_msg("Note: EVAL mode only observes WAF responses — it does not verify payload execution.")
            self.evaluate_wordlist(f"wordlists/{syntax}.txt")
        else:
            Utilities.print_error_msg(f"Couldn't parse {parameter} on {url}")

    '''
    --- Instance Methods ---
    '''
    def validate_url_parameter(self, url: str, parameter: str) -> bool:
        # Check if URL is not None
        if not url:
            return False

        # Parse the URL to extract query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Check if the parameter exists in the query string
        return parameter in query_params

    def evaluate_wordlist(self, wordlist_path: str) -> None:
        """
        This method accepts a wordlist file with one item per line, sends requests
        to the URL with each word as a parameter, and groups them by their response codes.

        :param wordlist_path: Path to the wordlist file.
        :return: None
        """
        response_groups = defaultdict(list)

        try:
            # Load wordlist
            with open(wordlist_path, 'r') as file:
                words = [line.strip() for line in file if line.strip()]

            Utilities.print_success_msg(f"Starting EVAL mode with {wordlist_path}")

            # Send requests with a progress bar
            for word in tqdm(words, desc="Sending requests", unit="request", ncols=100, position=0, leave=True):
                response_code = self.send_request(word)
                time.sleep(0.1) # Ensure a top 10req/s speed to avoid usage as DoS tool
                if response_code is not None:
                    response_groups[response_code].append(word)

            # Display grouped results
            for code, grouped_words in response_groups.items():
                Utilities.print_result_msg(f"Response Code {code}:")
                print(", ".join(grouped_words))

        except FileNotFoundError:
            Utilities.print_error_msg(f"File not found: {wordlist_path}")
        except Exception as e:
            Utilities.print_error_msg(f"An error occurred: {e}")

    def send_request(self, word: str) -> int or None:
        """
        Sends an HTTP GET request with the word as a query parameter and returns the response code.

        :param word: Word to send as a parameter.
        :return: HTTP response code or None if the request fails.
        """
        try:
            # Parse URL and update query parameter without duplication
            parsed_url = urlparse(self.url)
            query_params = parse_qs(parsed_url.query)
            query_params[self.parameter] = [word]

            new_query = urlencode(query_params, doseq=True)
            full_url = parsed_url._replace(query=new_query).geturl()

            response = requests.get(full_url)
            return response.status_code

        except requests.RequestException as e:
            Utilities.print_warning_msg(f"Request failed for word {word}: {e}")
            return None

