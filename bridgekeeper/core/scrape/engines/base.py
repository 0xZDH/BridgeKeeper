#!/usr/bin/env python3

import logging
import re
import requests  # type: ignore
import urllib3  # type: ignore
from typing import (
    Dict,
    List,
)

from bridgekeeper.utils.defaults import HTTP_HEADERS


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ScraperEngine:
    """Search Engine scraper engine base"""

    # Shared data sets
    progress = {}

    def __init__(
        self,
        company: str,
        depth: int = 5,
        timeout: float = 25,
        proxy: str = None,
        cookies: Dict[str, str] = None,
    ):
        """Initialize Scraper engine base.

        Arguments:
            company: name of company to scrape search engines for (i.e. `Example Ltd.`)
            depth: depth of pages to go for each search engine
            timeout: request timeout (HTTP)
            proxy: request proxy (HTTP)
            cookies: session cookies
        """
        # Inherited data sets
        self.company = company
        self.depth = depth
        self.timeout = timeout
        self.proxy = None if not proxy else {"http": proxy, "https": proxy}
        self.cookies = cookies

        # Create http session
        self.session = requests.Session()
        self._init_session()

        # Local data sets
        self.url = None
        self.engine = None

    def _init_session(self):
        """Initialize http session"""
        if self.cookies:
            self.session.cookies.update(self.cookies)

        if self.proxy:
            self.session.proxies.update(self.proxy)

    def _print_status(self):
        """Print the status of the current scraping - for all search engines"""
        try:
            total = self.depth * len(self.progress)
            current = sum(self.progress[k] for k in self.progress.keys())
            percent = (current / total) * 100.0
            print("[*] Progress: {0:.0f}%".format(percent), end="\r")

        except ZeroDivisionError:
            pass

    def _get_name(self, data: str) -> str:
        """When scraping the name from HTML, make sure to purge bad data.

        Arguments:
            data: name(s) found

        Returns:
            cleaned name(s)
        """
        return re.sub(" (-|–|\xe2\x80\x93).*", "", data)

    def _clean(self, data: str) -> str:
        """Clean the identified LinkedIn profile name by stripping
        invalid characters and/or Prefixes/Titles/Certs.

        Arguments:
            data: data from search engine results to cleaned

        Returns:
            cleaned/stripped data
        """
        # Replace invalid characters in names
        accents = {
            "a": "[àáâãäå]",
            "e": "[èéêë]",
            "i": "[ìíîï]",
            "o": "[òóôõö]",
            "u": "[ùúûü]",
            "y": "[ýÿ]",
            "n": "[ñ]",
            "ss": "[ß]",
        }
        for k, v in accents.items():
            data = re.sub("%s" % v, k, data)

        # Remove Prefixes/Titles/Certs in names
        for r in [
            ",.*",
            "\(.+?\)",
            "(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)",
            "I[IV][I]?",
            "'",
            "(Jr\.|Sr\.)",
        ]:
            data = re.sub(r, "", data)

        # Clean remaining unwanted data in names
        data = re.sub("\.", " ", data)
        data = re.sub("\s+", " ", data)

        chr_map = re.compile("[^a-zA-Z -]")
        data = chr_map.sub("", data)

        return data.strip()

    def _http_req(self, url: str) -> List[str]:
        """Send an HTTP request to a given search engine to scrape
        for LinkedIn profiles based on a company name.

        Arguments:
            url: url to request

        Returns:
            list of names found
        """
        try:
            response = self.session.get(
                url,
                headers=HTTP_HEADERS,
                timeout=self.timeout,
                verify=False,
            )

            return response.text

        except Exception as e:
            logging.error(f"Scraping failed for: {self.engine.title()}")
            logging.debug(f"{e}")
            return None
