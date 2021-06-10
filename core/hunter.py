#!/usr/bin/env python3
# Code via: https://github.com/nullg0re

import logging
import urllib3
import requests
from typing import Dict, Set

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Hunter(object):
    """Find username format and emails via Hunter.io."""

    HUNTER_EMAIL: str = "https://api.hunter.io/v2/domain-search?domain={DOMAIN}&api_key={KEY}&limit=100&offset={OFFSET}"
    HUNTER_FORMAT: str = (
        "https://api.hunter.io/v2/domain-search?domain={DOMAIN}&api_key={KEY}"
    )
    HEADERS: Dict[str, str] = {
        "DNT": "1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Connection": "keep-alive",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(
        self,
        domain: str,
        api_key: str = None,
        timeout: int = 25,
        proxy: str = None,
    ):
        """Initialize Hunter instance.

        Arguments:
            domain: target domain name for Hunter.io queries
            api_key: Hunter.io API key
            timeout: request timeout (HTTP)
            proxy: request proxy (HTTP)
        """
        self.session = requests.Session()
        self.domain = domain
        self.timeout = timeout
        self.api_key = api_key
        self.proxy = None if not proxy else {"http": proxy, "https": proxy}

    def hunt_format(self) -> str:
        """Query Hunter.io for username format based on the
        provided domain name.

        Returns:
            username format

        Excepts:
            KeyError: if no username format pattern found, return None
        """
        url = self.HUNTER_FORMAT.format(DOMAIN=self.domain, KEY=self.api_key)
        response = requests.get(
            url,
            headers=self.HEADERS,
            timeout=self.timeout,
            proxies=self.proxy,
            verify=False,
        )
        results = response.json()

        try:
            format_ = results["data"]["pattern"]
            return f"{format_}@{self.domain}"
        except KeyError:
            logging.error("Failed to get username format from Hunter.io")
            return None

    def hunt_emails(self) -> Set[str]:
        """Query Hunter.io for email addresses based on the provided
        domain name.

        Returns:
            set of email addresses

        Excepts:
            KeyError: if end of emails or no emails found, break
              loop
        """
        emails = set()
        offset = 0  # Starting offset
        while True:
            logging.debug(
                f"Attempting to get set of 100 email addresses at offset: {offset}"
            )

            # Request 100 emails per query
            url = self.HUNTER_EMAIL.format(
                DOMAIN=self.domain, KEY=self.api_key, OFFSET=offset
            )
            response = requests.get(
                url,
                headers=self.HEADERS,
                timeout=self.timeout,
                proxies=self.proxy,
                verify=False,
            )
            results = response.json()

            try:
                # As long as we get email results, continue
                if results["data"]["emails"]:
                    for email in results["data"]["emails"]:
                        emails.add(email["value"])

                    # Move query offset by 100
                    offset += 100

                # Otherwise, assume we hit the end and break
                else:
                    break

            except KeyError:
                logging.error("Error occured during Hunter.io email collection.")
                break

        return emails
