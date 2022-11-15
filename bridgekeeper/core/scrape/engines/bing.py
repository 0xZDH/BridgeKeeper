#!/usr/bin/env python3

import logging
import random
import time
from bs4 import BeautifulSoup  # type: ignore
from typing import List

from bridgekeeper.core.scrape.engines.base import ScraperEngine


class BingEngine(ScraperEngine):
    """Bing scraper engine"""

    def __init__(self, *args, **kwargs):
        """Initialize Bing Scraper instance"""
        super().__init__(*args, **kwargs)

        # Force required Bing cookie
        cookie = {"SRCHHPGUSR": "NRSLT=10"}
        if self.cookies:
            if "SRCHHPGUSR" not in self.cookies:
                self.session.cookies.update(cookie)

        else:
            self.session.cookies.update(cookie)

        base_url = "https://www.bing.com" if not self.proxy_url else self.proxy_url
        self.url = f"{base_url}/search?q=site%3Alinkedin.com%2Fin%2F+%22{self.company}%22&first="

        self.engine = "Bing"
        self.progress[self.engine] = 0

    def run(self) -> List[str]:
        """Scrape LinkedIn profiles based on a company name

        Returns:
            list of names found
        """
        logging.debug(f"Gathering names from {self.engine} (depth={self.depth})")

        names = []
        for index in range(self.depth):
            response = self._http_req(index * 14)

            if not response:
                break

            # Check for CAPTCHA in response
            if "CAPTCHA" not in response:
                self.progress[self.engine] += 1
                self._print_status()

                soup = BeautifulSoup(response, "lxml")

                # Find all names in the HTML response based on predefined keywords
                # to search for for each search engine
                search_results = soup.findAll("li", {"class": "b_algo"})
                if search_results:
                    for person in search_results:
                        try:
                            name = self._get_name(person.a.getText())
                            names.append(self._clean(name))

                        except:
                            pass

                else:
                    # Assume we hit the final page if there are no results
                    break

                # Search engine blacklist evasion technique
                # Sleep for random times between a half second and a full second
                time.sleep(round(random.uniform(1.0, 2.0), 2))

            else:
                self.progress[self.engine] = self.depth
                logging.error(f"CAPTCHA triggered for {self.engine}, halting scraping")
                break

        return names
