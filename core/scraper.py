#!/usr/bin/env python3

import re
import time
import random
import logging
import asyncio
import urllib3
import requests
from bs4 import BeautifulSoup  # type: ignore
from typing import Dict, List

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Scraper(object):
    """A Search Engine scraper for LinkedIn profile names."""

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
        company: str,
        depth: int = 5,
        timeout: int = 25,
        proxy: str = None,
        cookies: str = None,
    ):
        """Initialize Scraper instance.

        Arguments:
            company: name of company to scrape search engines for (i.e. `Example Ltd.`)
            depth: depth of pages to go for each search engine
            timeout: request timeout (HTTP)
            proxy: request proxy (HTTP)
            cookies: file name with Google CAPTCHA bypass cookie(s)
        """
        self.loop = asyncio.get_event_loop()
        self.employees = set()
        self.company = company
        self.depth = depth
        self.timeout = timeout
        self.proxy = None if not proxy else {"http": proxy, "https": proxy}
        self.cookies = None if not cookies else self.__set_cookie(cookies)
        self.data = {  # Data sets for each search engine
            "bing": {
                "url": "https://www.bing.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&first={INDEX}",
                "html": ["li", "class", "b_algo"],
                "idx": lambda x: x * 14,
            },
            "google": {
                "url": "https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&start={INDEX}",
                "html": ["h3", "class", "LC20lb"],
                "idx": lambda x: x * 10,
            },
            "yahoo": {
                "url": "https://search.yahoo.com/search?p=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&b={INDEX}",
                "html": ["a", "class", "ac-algo fz-l ac-21th lh-24"],
                "idx": lambda x: (x * 10) + 1,
            },
        }

        # Keep track of current depth of each search engine
        self.cur_d = {"google": 0, "yahoo": 0, "bing": 0}
        self.tot_d = self.depth * 3

    def __set_cookie(self, cookie_file: str) -> Dict[str, str]:
        """Read in cookie file and parse to a dictionary.

        Arguments:
            cookie_file: name of file containing cookies (one per line)

        Returns:
            dictionary of parsed cookies
        """
        cookies = {}
        cookies_ = [x.strip() for x in open(cookie_file).readlines()]
        for c in cookies_:
            for cookie in c.split(";"):
                if cookie:
                    cookie = cookie.strip()
                    name, value = cookie.split("=", 1)
                    cookies[name] = value

        return cookies

    def __print_status(self):
        """Print the status of the current scraping - for all search engines"""
        cur = sum(self.cur_d[k] for k in self.cur_d.keys())
        print("[*] Progress: {0:.0f}%".format((cur / self.tot_d) * 100.0), end="\r")

    def __get_name(self, data: str, se: str) -> str:
        """When scraping the name from HTML, make sure to purge bad data.

        Arguments:
            data: name(s) found
            se: serach engine where the name was found

        Returns:
            cleaned name(s)
        """
        if se == "bing":
            return re.sub(
                " (-|–|\xe2\x80\x93).*", "", data.findAll("a")[0].getText()
            )  # re.search('((?<=>)[A-Z].+?) - ', str(data)).group(1)

        return re.sub(" (-|–|\xe2\x80\x93).*", "", data.getText())

    def __clean(self, data: str) -> str:
        """Clean the identified LinkedIn profile name by stripping
        invalid characters and/or Prefixes/Titles/Certs.
        via: https://github.com/initstring/linkedin2username/blob/master/linkedin2username.py

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

    def http_req(self, se: str) -> List[str]:
        """Send an HTTP request to a given search engine to scrape
        for LinkedIn profiles based on a company name.

        Arguments:
            se: search engine to scrape

        Returns:
            list of names found
        """
        logging.info("Gathering names from %s (depth=%d)" % (se.title(), self.depth))

        # For the time being, only be concerned with CAPTCHA cookies when working
        # with Google
        cookies = None if se != "google" else self.cookies

        names = []
        for index in range(self.depth):
            resp = requests.get(
                self.data[se]["url"].format(
                    COMPANY=self.company, INDEX=(self.data[se]["idx"](index))
                ),
                headers=self.HEADERS,
                timeout=self.timeout,
                proxies=self.proxy,
                verify=False,
                cookies=cookies,
            )

            # Check for CAPTCHA in response
            if "solving the above CAPTCHA" not in resp.text:
                self.cur_d[se] += 1
                self.__print_status()

                soup = BeautifulSoup(resp.text, "lxml")
                search = self.data[se]["html"]

                # Find all names in the HTML response based on predefined keywords
                # to search for for each search engine
                search_results = soup.findAll(search[0], {search[1]: search[2]})
                if search_results:
                    for person in search_results:
                        name = self.__get_name(person, se)
                        names.append(self.__clean(name))
                else:
                    # Assume we hit the final page if there are no results
                    break

                # Search engine blacklist evasion technique
                # Sleep for random times between a half second and a full second
                time.sleep(round(random.uniform(1.0, 2.0), 2))

            else:
                self.cur_d[se] = self.depth
                logging.error(f"CAPTCHA triggered for {se}, halting scraper.")
                logging.debug(
                    "Try completing the CAPTCHA in a browser and then providing the Google cookies via --cookie"
                )
                break

        return names

    async def run(self):
        """Asynchronously send HTTP requests
        Here we are going to create three coroutines - one for each
        search engine. To avoid overloading the search engines and getting
        blacklisted, we are going to sleep after each request - if we don't
        contain the coroutines then asyncio will dump requests without waiting.
        """
        logging.info(
            "Starting %d coroutines to throttle requests to each search engine."
            % (len(self.data))
        )
        futures = [
            self.loop.run_in_executor(None, self.http_req, se)
            for se in self.data.keys()
        ]

        for data in asyncio.as_completed(futures):
            names = await data
            self.employees.update(names)
