#!/usr/bin/env python3

import re
import time
import random
import asyncio
import urllib3
import requests
from bs4 import BeautifulSoup
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""A Search Engine scraper for LinkedIn profile names."""

class Scraper:

    # Asyncio Event Loop
    loop = asyncio.get_event_loop()

    # List of found employee names - use a set to keep unique across search engines
    employees = set()

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:69.0) Gecko/20100101 Firefox/69.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    def __init__(self, company, depth=5, timeout=25, proxy=None):
        self.company = company
        self.depth   = depth
        self.timeout = timeout
        self.proxy   = None if not proxy else {
            "http": proxy, "https": proxy
        }
        self.data = { # Data sets for each search engine
            "bing": {
                "url":  'https://www.bing.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&first={INDEX}',
                "html": ["li", "class", "b_algo"],
                "idx":  lambda x: x * 14,
                "get":  self.__get_bing
            },
            "google": {
                "url":  'https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&start={INDEX}',
                "html": ["div", "class", "BNeawe vvjwJb AP7Wnd"],
                "idx":  lambda x: x * 10,
                "get":  self.__get_google
            },
            "yahoo": {
                "url":  'https://search.yahoo.com/search?p=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&b={INDEX}',
                "html": ["a", "class", "ac-algo fz-l ac-21th lh-24"],
                "idx":  lambda x: (x * 10) + 1,
                "get":  self.__get_yahoo
            }
        }

    def __get_google(self, data):
        return re.sub(' (-|–|\xe2\x80\x93).*', '', data.getText())

    def __get_yahoo(self, data):
        return re.sub(' (-|–|\xe2\x80\x93).*', '', data.getText())

    def __get_bing(self, data):
        return re.sub(' (-|–|\xe2\x80\x93).*', '', data.findAll('a')[0].getText()) # re.search('((?<=>)[A-Z].+?) - ', str(data)).group(1)

    def __remove(self, data):
        # Remove Prefixes/Titles/Certs in names and clean
        for r in [",.*", "\(.+?\)[ ]?", "(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)[ ]?", "I[IV][I]?[ ]?"]:
            data = re.sub(r, '', data)
        data = re.sub("\.", " ", data)
        data = re.sub("\s+", " ", data)
        return data.strip()

    def http_req(self, se):
        print('[*] Gathering names from %s (depth=%d)' % (se.title(), self.depth))
        names = []
        for index in range(self.depth):
            resp   = requests.get(self.data[se]["url"].format(COMPANY=self.company, INDEX=(self.data[se]["idx"](index))), headers=self.headers, timeout=self.timeout, proxies=self.proxy, verify=False)
            soup   = BeautifulSoup(resp.text, "lxml")
            search = self.data[se]["html"]

            for person in soup.findAll(search[0], {search[1]: search[2]}):
                name = self.data[se]["get"](person)
                names.append(self.__remove(name))

            # Search engine blacklist evasion technique
            # Sleep for random times between a half second and a full second
            time.sleep(round(random.uniform(0.5, 1.5), 2))

        return names

    async def run(self):
        """ Asynchronously send HTTP requests
        Here we are going to create three coroutines - one for each
        search engine. To avoid overloading the search engines and getting
        blacklisted, we are going to sleep after each request - if we don't
        contain the coroutines then asyncio will dump requests without waiting. """
        print("[*] Starting %d coroutines to throttle requests to each search engine." % (len(self.data)))
        futures = [
            self.loop.run_in_executor(
                None, self.http_req, url
            ) for url in self.data.keys()
        ]

        for data in asyncio.as_completed(futures):
            names = await data
            self.employees.update(names)