# Caliper

> "Measure twice, cut once."

## THIS IS A WIP!!!
Cloned versions may not be usable, stable versions will be on the releases tab.

## Legal & Ethical Considerations
Using Caliper to interact with unauthorized systems is illegal and unethical. This tool is meant solely for educational and research purposes within controlled environments where you have explicit permission. Acceptable use cases include:

- Security Research
- Penetration Testing & Red Teaming Engagements (with proper authorization)
- Ethical Hacking scenarios where any parties involved consent to its use

Unauthorized use of Caliper may violate cybercrime laws, including but not limited to the Computer Fraud and Abuse Act (CFAA) and General Data Protection Regulation (GDPR). Misuse can lead to legal consequences, including criminal charges and civil liability.

Additionally, improper use of Caliper could pose serious security risks, such as denial of service.

By using Caliper, you agree to use it ethically and legally. You take full responsibility for how this tool is used. This tool must never be used for unauthorized access, military applications or unlawful financial gain.

## Evasion Vector Mode
Focuses on finding methods to bypass WAF restrictions by targeting a user-defined string in an HTTP request. The user specifies the HTTP method to use, the evasion vector to employ, the string causing the WAF blockage, and the HTTP response code the WAF gives when the request is blocked. A successful bypass is determined when the HTTP response code changes after applying the vector, and if the match-content option is enabled, when the body of the response changes as well (useful if the WAF blockage response code is 200-like).

### Vectors
#### Junk Data Injection (JDI)
The Burp Suite plugin nowafpls (https://github.com/assetnote/nowafpls) popularized the junk-data WAF evasion technique and offered some guidelines on how much data to insert depending on the Firewall implemented. 

However it's not always posible to know how much junk data will be needed to succesfuly avoid a Firewall. Caliper offers an streamlined way of discovering the ammount of data that can be used to allow a previously-blocked payload passthrough

By this vector this tool also doubles as a network stress-tester

#### Origin Header Tampering (OHT)
WAFs can be caused to not inspect packages by modifying HTTP headers like X-Originating-IP, X-Forwarded-For, X-Remote-IP, X-Remote-Addr to local values such as 127.0.0.1 and 0.0.0.0 if the WAF is designed to "trust itself" or upstream proxies.

#### HTTP Verb Swap (HVS)
A WAF may not evaluate requests with HTTP method PUT when it would evaluate the same request if it were using POST.

#### Random Payload Capitalization (RPC)
Payloads that are not case-sensitive (such as potential SQLi) can sometimes pass regex matching if they are randomly capitalized.

## Evaluation Mode
Focus on finding specific parts of a request that are either not blocked or reflected by the WAF. Instead of just trying to bypass the WAF with specific data (such as with Vector mode), you can use Eval Mode to set a GET parameter to identify useful items that can slip through. This is especially helpful for creating payloads like XSS attacks.

These useful items could include:

- JavaScript snippets
- HTML tags
- SQL fragments
- Special characters

Eval Mode helps you figure out what works and makes it easier to generate the right payloads for your testing.
