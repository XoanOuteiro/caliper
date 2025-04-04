'''
-- Caliper
-- author/s: @XoanOuteiro
'''

from utils.utilities import Utilities
import re

class ReqHandler:
    def __init__(self, file_path, scheme):
        self.http_verb = None
        self.url = None
        self.headers = {}
        self.body = None
        self.host = None
        self.scheme = scheme
        self.full_url = None
        self._parse_file(file_path)

    def _parse_file(self, file_path):
        """
        Parse the file content and separate it into HTTP verb, URL, headers, and body.
        """

        try:
            with open(file_path, 'r') as file:
                content = file.read()
        except Exception as error:
            Utilities.print_error_msg("File not found.")

        # Regex to match the HTTP verb and URL (first line in the request)
        request_line_match = re.match(r"(POST|GET|PUT|DELETE|PATCH)\s+([^\s]+)\s+HTTP/1.1", content)
        if request_line_match:
            self.http_verb = request_line_match.group(1)

            if self.http_verb == "GET":
                Utilities.print_error_msg("GET requests are not yet supported under VEC mode.")
            else:
                Utilities.print_success_msg(f"Successfully parsed HTTP Verb as: {str(self.http_verb)}")

            self.url = request_line_match.group(2)
            Utilities.print_success_msg(f"Successfully parsed PATH as: {str(self.url)}")

        # Regex to match headers (lines after the request line until an empty line)
        header_lines = re.findall(r"([^\r\n:]+):\s*([^\r\n]+)", content)
        self.headers = {key.strip(): value.strip() for key, value in header_lines}

        # Extract host from headers (use 'Host' header)
        self.host = self.headers.get('Host')
        if not self.host:
            Utilities.print_error_msg("No Host header found in the request.")
        else:
            Utilities.print_success_msg(f"Successfully parsed host as: {str(self.host)}")
        
        # Check if at least one 'Content-Type' header is present
        if 'Content-Type' not in self.headers:
            Utilities.print_error_msg("No Content-type header found.")

        # Construct the full URL (scheme + host + path)
        self.full_url = f"{self.scheme}://{self.host}{self.url}"
        Utilities.print_success_msg(f"Successfully built URL as: {str(self.full_url)}")

        # Body is everything after an empty line
        body_match = re.search(r"\r?\n\r?\n(.*)", content, re.DOTALL)
        if body_match:
            self.body = body_match.group(1).strip()
            Utilities.print_success_msg(f"Successfully parsed body")
