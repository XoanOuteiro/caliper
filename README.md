# Caliper

> "Measure twice, cut once."

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
