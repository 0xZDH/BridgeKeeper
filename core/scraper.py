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

    def __init__(self, company, cookies=None, depth=5, timeout=25, proxy=None):
        self.company = company
        self.depth   = depth
        self.timeout = timeout
        self.cookies = None if not cookies else self.__set_cookie(cookies)
        self.proxy   = None if not proxy else {
            "http": proxy, "https": proxy
        }
        self.data = { # Data sets for each search engine
            "bing": {
                "url":  'https://www.bing.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&first={INDEX}',
                "html": ["li", "class", "b_algo"],
                "idx":  lambda x: x * 14
            },
            "google": {
                "url":  'https://www.google.com/search?q=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&start={INDEX}',
                "html": ["h3", "class", "LC20lb"],
                "idx":  lambda x: x * 10
            },
            "yahoo": {
                "url":  'https://search.yahoo.com/search?p=site%3Alinkedin.com%2Fin%2F+%22at+{COMPANY}%22&b={INDEX}',
                "html": ["a", "class", "ac-algo fz-l ac-21th lh-24"],
                "idx":  lambda x: (x * 10) + 1
            }
        }

        # Keep track of current depth of each search engine
        self.cur_d = {'google': 0, 'yahoo': 0, 'bing': 0}
        self.tot_d = self.depth * 3

    def __set_cookie(self, cookie_file):
        cookies  = {}
        _cookies = [x.strip() for x in open(cookie_file).readlines()]
        for _cook in _cookies:
            for cookie in _cook.split(';'):
              cookie = cookie.strip()
              name,value = cookie.split('=', 1)
              cookies[name] = value

        return cookies

    def __print_status(self):
        cur = sum(self.cur_d[k] for k in self.cur_d.keys())
        print('[*] Progress: {0:.0f}%'.format((cur / self.tot_d) * 100.0), end='\r')

    def __get_name(self, data, se):
        if se == 'bing':
            return re.sub(' (-|–|\xe2\x80\x93).*', '', data.findAll('a')[0].getText()) # re.search('((?<=>)[A-Z].+?) - ', str(data)).group(1)

        return re.sub(' (-|–|\xe2\x80\x93).*', '', data.getText())

    def __clean(self, data):
        # From: https://github.com/initstring/linkedin2username/blob/master/linkedin2username.py
        accents = {
            'a':  u"[àáâãäå]",
            'e':  u"[èéêë]",
            'i':  u"[ìíîï]",
            'o':  u"[òóôõö]",
            'u':  u"[ùúûü]",
            'y':  u"[ýÿ]",
            'n':  u"[ñ]",
            'ss': u"[ß]"
        }
        for k,v in accents.items():
            data = re.sub(u"%s" % v, k, data)

        # Remove Prefixes/Titles/Certs in names and clean
        for r in [",.*", "\(.+?\)", "(Mr\.|Mrs\.|Ms\.|Dr\.|Prof\.)", "I[IV][I]?", "'", "(Jr\.|Sr\.)"]:
            data = re.sub(r, '', data)
        data = re.sub("\.", ' ', data)
        data = re.sub("\s+", ' ', data)

        chr_map = re.compile("[^a-zA-Z -]")
        data    = chr_map.sub('', data)

        return data.strip()

    def http_req(self, se):
        print('[*] Gathering names from %s (depth=%d)' % (se.title(), self.depth))
        names   = []
        cookies = None if se != "google" else self.cookies
        for index in range(self.depth):
            resp   = requests.get(self.data[se]["url"].format(COMPANY=self.company, INDEX=(self.data[se]["idx"](index))), headers=self.headers, timeout=self.timeout, proxies=self.proxy, verify=False, cookies=cookies)
            if 'solving the above CAPTCHA' not in resp.text:
                self.cur_d[se] += 1
                self.__print_status()

                soup   = BeautifulSoup(resp.text, "lxml")
                search = self.data[se]["html"]

                if soup.findAll(search[0], {search[1]: search[2]}):
                    for person in soup.findAll(search[0], {search[1]: search[2]}):
                        name = self.__get_name(person, se)
                        names.append(self.__clean(name))

                else:
                    # Assume we hit the final page
                    break

                # Search engine blacklist evasion technique
                # Sleep for random times between a half second and a full second
                time.sleep(round(random.uniform(1.0, 2.0), 2))

            else:
                self.cur_d[se] = self.depth
                print("[!] CAPTCHA triggered for %s, stopping scrape..." % se)
                print("[*] Try completing the CAPTCHA in a browser and then providing the Google cookies via --cookie")
                break

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
                None, self.http_req, se
            ) for se in self.data.keys()
        ]

        for data in asyncio.as_completed(futures):
            names = await data
            self.employees.update(names)