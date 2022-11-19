#!/usr/bin/env python3
# Code via: https://github.com/nullg0re

import logging
import requests  # type: ignore
import urllib3  # type: ignore
from typing import Set

from bridgekeeper.utils.defaults import HTTP_HEADERS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Hunter(object):
    """Find username format and emails via Hunter.io."""

    HUNTER_BASE = "https://api.hunter.io/v2/domain-search"

    def __init__(
        self,
        domain: str,
        api_key: str,
        timeout: float = 25,
        proxy: str = None,
    ):
        """Initialize Hunter instance.

        Arguments:
            domain: target domain name for Hunter.io queries
            api_key: Hunter.io API key
            timeout: request timeout (HTTP)
            proxy: request proxy (HTTP)
        """
        self.domain = domain
        self.api_key = api_key
        self.timeout = timeout
        self.proxy = None if not proxy else {"http": proxy, "https": proxy}

        self.url = f"{self.HUNTER_BASE}?domain={self.domain}&api_key={self.api_key}"
        self.session = requests.Session()

    def hunt_format(self) -> str:
        """Query Hunter.io for username format based on the
        provided domain name.

        Returns:
            username format

        Raises:
            KeyError: if no username format pattern found, return None
        """
        try:
            response = requests.get(
                self.url,
                headers=HTTP_HEADERS,
                timeout=self.timeout,
                proxies=self.proxy,
                verify=False,
            )
            results = response.json()

            format_ = results["data"]["pattern"]
            return f"{format_}@{self.domain}"

        except Exception as e:
            logging.error(f"Failed to get username format from Hunter.io")
            logging.debug(f"{e}")
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
            logging.debug(f"Attempting to get set of 100 email addresses at offset: {offset}")  # fmt: skip

            # Request 100 emails per query
            url = f"{self.url}&limit=100&offset={offset}"

            try:
                response = requests.get(
                    url,
                    headers=HTTP_HEADERS,
                    timeout=self.timeout,
                    proxies=self.proxy,
                    verify=False,
                )
                results = response.json()

                # As long as we get email results, continue
                if results["data"]["emails"]:
                    for email in results["data"]["emails"]:
                        emails.add(email["value"])

                    # Move query offset by 100
                    offset += 100

                # Otherwise, assume we hit the end and break
                else:
                    break

            except Exception as e:
                logging.error(f"An error occured during Hunter.io email collection")
                logging.debug(f"{e}")
                break

        return emails
