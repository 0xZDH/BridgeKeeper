#!/usr/bin/env python3

import logging
import random
import re
import time
from typing import List

from bridgekeeper.core.scrape.engines.base import ScraperEngine
from bridgekeeper.utils.helper import check_substring


class DuckDuckGoEngine(ScraperEngine):
    """DuckDuckGo scraper engine"""

    def __init__(self, *args, **kwargs):
        """Initialize DuckDuckGo Scraper instance"""
        super().__init__(*args, **kwargs)

        # Init engine
        self.engine = "DuckDuckGo"
        self.progress[self.engine] = 0
        self.url = f"https://links.duckduckgo.com/d.js?q=site%3Alinkedin.com%2Fin%2F%20%22%2D%20{self.company}%22&s="

        # Send initial request to get
        self.token = None
        self._init_req()

    def _init_req(self):
        """Send initial request to retrieve custom JavaScript generated token"""
        url_ = f"https://duckduckgo.com/?q=site%3Alinkedin.com%2Fin%2F%20%22%2D%20{self.company}%22&t=h_"

        response = self._http_req(url_)
        if response:
            token_regex = re.search("vqd='(.+?)';", response)
            if token_regex:
                self.token = token_regex.group(1)

    def run(self) -> List[str]:
        """Scrape DuckDuckGo search engine for LinkedIn profiles based
        on a company name

        Returns:
            list of names found
        """
        # Custom DuckDuckGo handling as search requests require an initial
        # token
        if not self.token:
            logging.error("Could not retrieve DuckDuckGo search token, ending coroutine")  # fmt: skip
            return []

        logging.debug(f"Gathering names from {self.engine} (depth={self.depth})")

        i = 0
        names = []
        for _ in range(self.depth):
            # Update current index
            url_ = self.url + str(i)
            url_ += f"&vqd={self.token}"

            response = self._http_req(url_)

            if not response:
                break

            # Check for CAPTCHA in response
            if "CAPTCHA" not in response:
                self.progress[self.engine] += 1
                self._print_status()

                # DuckDuckGo has slightly different handling than the other
                # search engines - instead of an HTML response with results,
                # the results are returned via the Content-Type: x-javascript.
                # Within the JavaScript, there is JSON data structures for each
                # result, but instead of trying to parse out the JSON and then
                # load it as a dictionary - it appears that all result titles
                # have a key of "t". This appears to be the only visible object
                # that has a "t" value - so we can just regex the response for
                # all titles...
                title_regex = re.findall('"t":"(.+?)",', response)

                if title_regex:
                    # Account for end of search results via 'EOF'
                    if len(title_regex) == 1 and "EOF" in title_regex[0]:
                        # Adjust progress bar accordingly
                        if self.progress[self.engine] < self.depth:
                            self.progress[self.engine] = self.depth
                            self._print_status()

                        break

                    # It seems there isn't a super consistent way to move from
                    # page to page as the results are dynamically loaded in chunks,
                    # so we need to get the number of results from the current
                    # request and shift the index accordingly
                    i += len(title_regex)

                    for person in title_regex:
                        try:
                            name = self._get_name(person)
                            name = self._clean(name)

                            # While maybe not the best approach, attempt to avoid
                            # found names that are just job titles ending with the
                            # company and/or LinkedIn
                            if (
                                not check_substring(name, self.company)  # fmt: skip
                                and not check_substring(name, "linkedin")  # fmt: skip
                            ):
                                names.append(name)

                        except:
                            pass

                else:
                    # Assume we hit the final page if there are no results
                    break

                # Search engine blacklist evasion technique
                # Sleep for random times between a half second and a full second
                time.sleep(round(random.uniform(1.0, 2.0), 2))

            else:
                logging.error(f"CAPTCHA triggered for {self.engine}, ending coroutine")

                # Adjust progress bar accordingly
                if self.progress[self.engine] < self.depth:
                    self.progress[self.engine] = self.depth
                    self._print_status()

                break

        return names
