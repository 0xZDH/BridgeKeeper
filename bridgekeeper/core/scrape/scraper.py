#!/usr/bin/env python3

import asyncio
import logging

from bridgekeeper.core.scrape.engines import (
    BingEngine,
    GoogleEngine,
    YahooEngine,
)


class Scraper:
    """A Search Engine scraper for LinkedIn profile names."""

    def __init__(
        self,
        company: str,
        depth: int = 5,
        timeout: float = 25,
        proxy: str = None,
        bing_cookies: str = None,
        google_cookies: str = None,
        yahoo_cookies: str = None,
    ):
        """Initialize Scraper instance.

        Arguments:
            company: name of company to scrape search engines for (i.e. `Example Ltd.`)
            depth: depth of pages to go for each search engine
            timeout: request timeout (HTTP)
            proxy: request proxy (HTTP)
            bing_cookies: bing cookies
            google_cookies: google cookies
            yahoo_cookies: yahoo cookies
        """
        self.loop = asyncio.get_event_loop()
        self.employees = set()

        self.company = company
        self.depth = depth
        self.timeout = timeout
        self.proxy = proxy

        # FireProx proxy URLs
        self.bing_cookies = bing_cookies
        self.google_cookies = google_cookies
        self.yahoo_cookies = yahoo_cookies

    async def run(self):
        """Asynchronously send HTTP requests
        Here we are going to create multiple coroutines - one for each
        search engine. To avoid overloading the search engines and getting
        blacklisted, we are going to sleep after each request - if we don't
        contain the coroutines then asyncio will dump requests without waiting.
        """
        logging.debug(f"Launching scraper coroutines")

        # Asyncio Event Loop
        loop = asyncio.get_event_loop()

        runner_args = {
            "company": self.company,
            "depth": self.depth,
            "timeout": self.timeout,
            "proxy": self.proxy,
            "cookies": None,
        }

        futures = []
        engines = [BingEngine, GoogleEngine, YahooEngine]

        for engine in engines:
            # Setup FireProx proxying
            if engine == BingEngine:
                runner_args["cookies"] = self.bing_cookies
            elif engine == GoogleEngine:
                runner_args["cookies"] = self.google_cookies
            elif engine == YahooEngine:
                runner_args["cookies"] = self.yahoo_cookies

            engine_runner = engine(**runner_args)
            futures.append(loop.run_in_executor(None, engine_runner.run))

            # Reset cookies per engine
            if runner_args["cookies"]:
                runner_args["cookies"] = None

        for data in asyncio.as_completed(futures):
            names = await data
            self.employees.update(names)
