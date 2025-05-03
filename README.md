# Caliper Suite

```
________  ________  ___       ___  ________  _______   ________     
|\   ____\|\   __  \|\  \     |\  \|\   __  \|\  ___ \ |\   __  \    
\ \  \___|\ \  \|\  \ \  \    \ \  \ \  \|\  \ \   __/|\ \  \|\  \   
 \ \  \    \ \   __  \ \  \    \ \  \ \   ____\ \  \_|/_\ \   _  _\  
  \ \  \____\ \  \ \  \ \  \____\ \  \ \  \___|\ \  \_|\ \ \  \\  \| 
   \ \_______\ \__\ \__\ \_______\ \__\ \__\    \ \_______\ \__\\ _\ 
    \|_______|\|__|\|__|\|_______|\|__|\|__|     \|_______|\|__|\|__|
```

Project by XoanOuteiro @ The Smoking GNU (thesmokinggnu.org)

The Caliper Suite helps pentesters and system administrators identify potential weaknesses in Web Application Firewalls (WAFs), offering insights into how attackers might exploit underlying vulnerabilities.

There´s an article on this apps usage at my webpage:

[WAF Benchmarking With Caliper.py](https://xoanouteiro.dev/posts/es_caliper_waf_benchmarking/)


## THIS IS A WIP!!!
Cloned versions may not be usable, stable versions will be on the releases tab.

Current development state:

| Mode | Vector/Syntax | State |
| --- | --- | --- |
| VEC | JDI | :white_check_mark: |
| VEC | OHT | :white_check_mark: |
| VEC | HVS | :white_check_mark: |
| VEC | RPC | :white_check_mark: |
| EVAL | HTML | :white_check_mark: |
| EVAL | SQL | :white_check_mark: |
| EVAL | LFI | :white_check_mark: |

TBI = To Be Implemented

As of Beta-0.1 all base modules are implemented and tested.

## Legal & Ethical Considerations
Using Caliper to interact with unauthorized systems is illegal and unethical. This tool is meant solely for educational and research purposes within controlled environments where you have explicit permission. Acceptable use cases include:

- Security Research
- Penetration Testing & Red Teaming Engagements (with proper authorization)
- Ethical Hacking scenarios where any parties involved consent to its use

Unauthorized use of Caliper may violate cybercrime laws, including but not limited to the Computer Fraud and Abuse Act (CFAA) and General Data Protection Regulation (GDPR). Misuse can lead to legal consequences, including criminal charges and civil liability.

Additionally, improper use of Caliper could pose serious security risks, such as denial of service.

By using Caliper, you agree to use it ethically and legally. You take full responsibility for how this tool is used. This tool must never be used for unauthorized access, military applications or unlawful financial gain.

## Project Structure

```
.
├── caliper.py
├── install.sh
├── interfacing
│   └── argparser.py
├── modules
│   ├── evaluator.py
│   ├── hvs.py
│   ├── jdi.py
│   ├── oht.py
│   └── rpc.py
├── README.md
├── requirements.txt
├── templates
│   └── default.py
├── test_requests
│   ├── datai.txt
│   └── json.txt
├── utils
│   ├── reqhandler.py
│   └── utilities.py
└── wordlists
    ├── HTML.txt
    ├── LFI.txt
    ├── quotes.txt
    └── SQL.txt
```

## Installation

1.  Clone the repository:

    ``` bash
    git clone https://github.com/XoanOuteiro/caliper
    cd caliper
    ```

1. (Optional) In the event of missing dependencies, there are two options:
    using a system-wide install (the script automatically detects Debian and Arch based OSs for the apropiate package manager):

    ``` bash
    chmod +x install.sh && ./install.sh
    ```

    Or if you are using a venv, via pip:

    ``` bash
    pip install -r requirements.txt
    ```
## Evasion Vector Mode
Focuses on finding methods to bypass WAF restrictions by targeting a user-defined string in an HTTP request. The user specifies the HTTP method to use, the evasion vector to employ, the string causing the WAF blockage, and the HTTP response code the WAF gives when the request is blocked. A successful bypass is determined when the HTTP response code changes after applying the vector, and if the match-content option is enabled, when the body of the response changes as well (useful if the WAF blockage response code is 200-like).

### Vectors
#### Junk Data Injection (JDI)
The Burp Suite plugin nowafpls (https://github.com/assetnote/nowafpls) popularized the junk-data WAF evasion technique and offered some guidelines on how much data to insert depending on the Firewall implemented. 

However it's not always posible to know how much junk data will be needed to succesfuly avoid a Firewall. Caliper offers an streamlined way of discovering the ammount of data that can be used to allow a previously-blocked payload passthrough

By this vector this tool also doubles as a network stress-tester

An example of running this command would be:

``` bash
python caliper.py VEC JDI --protocol http --segment "'OR='1'='1" --code 403 --request-file test_requests/datai.txt --min-size 10 --max-size 142000 --match-content
```

Where min-size and max-size are in bytes.


#### Origin Header Tampering (OHT)
WAFs can be caused to not inspect packages by modifying HTTP headers like X-Originating-IP, X-Forwarded-For, X-Remote-IP, X-Remote-Addr to local values such as 127.0.0.1 and 0.0.0.0 if the WAF is designed to "trust itself" or upstream proxies.
OHT will also test all combinations of 2 Origin-like headers.

An example on running this module:

``` bash
python caliper.py VEC OHT --protocol http --segment "'OR='1'='1" --code 403 --request-file test_requests/datai.txt
```

#### HTTP Verb Swap (HVS)
A WAF may not evaluate requests with HTTP method PUT when it would evaluate the same request if it were using POST.
405 response codes are NOT counted as potential bypasses, you may enable testing for GET and OPTIONS by uncommenting them from the source code.
Content matching works with HVS but it will cause false positives.

An example on running this module:

``` bash
python caliper.py VEC HVS --protocol http --segment "'OR='1'='1" --code 403 --request-file test_requests/datai.txt
```

#### Random Payload Capitalization (RPC)
Payloads that are not case-sensitive (such as potential SQLi) can sometimes pass regex matching if they are randomly capitalized.

An example on running this module:

``` bash
python caliper.py VEC RPC --protocol http --segment "'OR='1'='1" --code 403 --request-file test_requests/datai.txt
```

## Evaluation Mode
Focus on finding specific parts of a request that are either not blocked or reflected by the WAF. Instead of just trying to bypass the WAF with specific data (such as with Vector mode), you can use Eval Mode to set a GET parameter to identify useful items that can slip through. This is especially helpful for creating payloads like XSS attacks.

Eval Mode helps you figure out what works and makes it easier to generate the right payloads for your testing.

For some examples:

Testing for simple XSS bypassing with the HTML dictionary:

``` bash
python caliper.py EVAL --url https://xoanouteiro.dev?query=test&info=1 --parameter query --syntax-type HTML
```
Testing for path traversal and local file inclusion via the LFI dictionary:

``` bash
python caliper.py EVAL --url https://xoanouteiro.dev?query=test&info=1 --parameter query --syntax-type LFI
```

Testing for SQLi:

``` bash
python caliper.py EVAL --url https://xoanouteiro.dev?query=test&info=1 --parameter query --syntax-type SQL
```

Keep in mind you can always expand the testing pool by writing new lines into the dictionaries at ./wordlists/
