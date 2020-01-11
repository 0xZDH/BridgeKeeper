#!/usr/bin/env python3

import json
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#
# Code provided by: https://github.com/aslarchergore
#

# A free Hunter.io account can be set up: https://hunter.io/pricing

class Hunter:

    hunter_format = "https://api.hunter.io/v2/domain-search?domain={DOMAIN}&api_key={KEY}"
    hunter_email  = "https://api.hunter.io/v2/domain-search?domain={DOMAIN}&api_key={KEY}&limit=100&offset={OFFSET}"

    # Storage for emails identified
    emails = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    def __init__(self, domain, api_key=None, timeout=25, proxy=None):
        self.session = requests.Session()
        self.domain  = domain
        self.timeout = timeout
        self.api_key = api_key
        self.proxy   = None if not proxy else {
            "http": proxy, "https": proxy
        }

    def hunt_format(self):
        print("[*] Gathering email format from Hunter.io")
        url  = self.hunter_format.format(DOMAIN=self.domain, KEY=self.api_key)
        resp = self.session.get(url, headers=self.headers, timeout=self.timeout, proxies=self.proxy, verify=False)
        results = resp.json()

        try:
            _format = results["data"]["pattern"]
            return "%s@%s" % (_format, self.domain)

        except KeyError as e:
            print("[!] Failed to get email format from Hunter.io")
            return None

    def hunt_emails(self):
        print("[*] Gathering emails from Hunter.io")
        offset = 0
        msg    = "first"
        while True:
            print("[*] Attempting to get the %s set of 100 email addresses" % msg)
            url  = self.hunter_email.format(DOMAIN=self.domain, KEY=self.api_key, OFFSET=offset)
            resp = requests.get(url, headers=self.headers, timeout=self.timeout, proxies=self.proxy, verify=False)
            results = resp.json()

            try:
                if results["data"]["emails"]:
                    for email in results["data"]["emails"]:
                        self.emails.add(email["value"])

                    offset += 100
                    if msg == "first":
                        msg = "next"

                else:
                    break

            except KeyError as e:
                print("[!] Error occured during email gathering.")
                break