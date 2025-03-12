# Caliper

> "Measure twice, cut once."

## Legal & Ethical Considerations
Using Caliper to interact with unauthorized systems is illegal and unethical. This tool is meant solely for educational and research purposes within controlled environments where you have explicit permission. Acceptable use cases include:

- Security Research
- Penetration Testing & Red Teaming Engagements (with proper authorization)
- Ethical Hacking scenarios where any parties involved consent to its use

Unauthorized use of Caliper may violate cybercrime laws, including but not limited to the Computer Fraud and Abuse Act (CFAA) and General Data Protection Regulation (GDPR). Misuse can lead to legal consequences, including criminal charges and civil liability.

Additionally, improper use of Caliper could pose serious security risks, such as denial of service.

By using Caliper, you agree to use it ethically and legally. You take full responsibility for how this tool is used. This tool must never be used for unauthorized access, military applications or unlawful financial gain.

## Vectors
### Junk Data Injection (JDI)
The Burp Suite plugin nowafpls (https://github.com/assetnote/nowafpls) popularized the junk-data WAF evasion technique and offered some guidelines on how much data to insert depending on the Firewall implemented. 

However it's not always posible to know how much junk data will be needed to succesfuly avoid a Firewall. Caliper offers an streamlined way of discovering the ammount of data that can be used to allow a previously-blocked payload passthrough

By this vector this tool also doubles as a network stress-tester

### Origin Header Tampering (OHT)
WAFs can be caused to not inspect packages by modifying HTTP headers like X-Originating-IP, X-Forwarded-For, X-Remote-IP, X-Remote-Addr to local values such as 127.0.0.1 and 0.0.0.0 if the WAF is designed to "trust itself" or upstream proxies.

### HTTP Verb Swap (HVS)
A WAF may not evaluate requests with HTTP method PUT when it would evaluate the same request if it were using POST.

### Random Payload Capitalization (RPC)
Payloads that are not case-sensitive (such as potential SQLi) can sometimes pass regex matching if they are randomly capitalized.

