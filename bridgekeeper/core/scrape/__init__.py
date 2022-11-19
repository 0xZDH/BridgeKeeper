#!/usr/bin/env python3

import logging
from typing import (
    Dict,
    List,
)

from bridgekeeper.core.scrape.scraper import Scraper
from bridgekeeper.utils.defaults import START_SCRIPT


def scrape(
    company: str,
    output_dir: str,
    depth: int = 5,
    timeout: float = 25,
    proxy: str = None,
    bing_cookies: Dict[str, str] = None,
    duckduckgo_cookies: Dict[str, str] = None,
    google_cookies: Dict[str, str] = None,
    yahoo_cookies: Dict[str, str] = None,
) -> List[str]:
    """Scrape Bing, DuckDuckGo, Google, and Yahoo for LinkedIn profiles
    by invoking the Scraper module. Write found names to a file in a
    designated output directory.

    Arguments:
        company: name of company to scrape (i.e. 'Example Ltd.')
        output_dir: directory where to write names file to
        depth: number of pages deep to scrape per search engine
        timeout: request timeout (HTTP)
        proxy: request proxy (HTTP)
        *_cookies: search engine cookies

    Returns:
        list of names
    """
    scraper = Scraper(
        company=company,
        depth=depth,
        timeout=timeout,
        proxy=proxy,
        bing_cookies=bing_cookies,
        duckduckgo_cookies=duckduckgo_cookies,
        google_cookies=google_cookies,
        yahoo_cookies=yahoo_cookies,
    )
    scraper.loop.run_until_complete(scraper.run())

    # Create file to write users to: <example_ltd>_names_<date>.txt
    company = company.strip().strip(".")
    company_fname = company.replace(".", "_").replace(" ", "_")
    output_file = f"{output_dir}/{company_fname}_names_{START_SCRIPT}.txt"

    if scraper.employees:
        logging.debug(f"Writing names to the following file: {output_file}")
        with open(output_file, "a") as f:
            for name in scraper.employees:
                f.write(f"{name}\n")

    return scraper.employees
