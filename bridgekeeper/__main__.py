#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import time
import sys
from pathlib import Path

from bridgekeeper import (
    __banner__,
    __version__,
)
from bridgekeeper.core.hunt import hunt
from bridgekeeper.core.scrape import scrape
from bridgekeeper.core.transform import transform
from bridgekeeper.utils.defaults import START_SCRIPT
from bridgekeeper.utils.helper import (
    check_file,
    cookie_file_to_dict,
    cookie_str_to_dict,
    file_to_list,
)
from bridgekeeper.utils.logger import init_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments

    Returns:
        argument namespace
    """
    parser = argparse.ArgumentParser(description=f"BridgeKeeper - v{__version__}")

    # Allow a user to scrape names or just convert an already generated list of names
    target_args = parser.add_argument_group(title="Target(s)")
    target_group = target_args.add_mutually_exclusive_group()
    target_group.add_argument(
        "-c",
        "--company",
        type=str,
        help="target company to search for LinkedIn profiles (e.g. 'Example Ltd.')",
    )
    target_group.add_argument(
        "-n",
        "--names",
        type=str,
        help=(
            "string (comma delimited) or file containing names to be converted to "
            "usernames (format: 'First (M) Last')"
        ),
    )

    # Require a user to specify whether to pull a username format from Hunter.io
    # or specify a format manually
    format_args = parser.add_argument_group(title="Username Formatting")
    format_group = format_args.add_mutually_exclusive_group()
    format_group.add_argument(
        "-f",
        "--format",
        type=str,
        help=(
            "username format "
            "(format identifiers: {first}, {middle}, {last}, {f}, {m}, {l}, [#])"
        ),
    )
    format_group.add_argument(
        "-a",
        "--api",
        type=str,
        help="hunter.io API key for email format identification and email scraping",
    )
    format_args.add_argument(
        "-d",
        "--domain",
        type=str,
        help=(
            "domain name of target company for hunter.io email format "
            "identification and email scraping"
        ),
    )
    format_args.add_argument(
        "--lower",
        action="store_true",
        help="force usernames to all lower case",
    )
    format_args.add_argument(
        "--upper",
        action="store_true",
        help="force usernames to all upper case",
    )

    search_args = parser.add_argument_group(title="Search Engine Configuration")
    search_args.add_argument(
        "--depth",
        type=int,
        help="number of pages deep to search each search engine (Default: 5)",
        default=5,
    )
    search_args.add_argument(
        "--bing-cookies",
        type=str,
        help="string or cookie file for Bing search engine",
    )
    search_args.add_argument(
        "--google-cookies",
        type=str,
        help="string or cookie file for Google search engine",
    )
    search_args.add_argument(
        "--yahoo-cookies",
        type=str,
        help="string or cookie file for Yahoo search engine",
    )

    http_args = parser.add_argument_group(title="HTTP Configuration")
    http_args.add_argument(
        "--timeout",
        type=float,
        help="HTTP request timeout in seconds (Default: 25 seconds)",
        default=25,
    )
    http_args.add_argument(
        "--proxy",
        type=str,
        help="proxy to pass HTTP traffic through: `host:port`",
    )

    output_args = parser.add_argument_group(title="Output Configuration")
    output_args.add_argument(
        "-o",
        "--output",
        type=str,
        help="directory to write output files to (Default: output)",
        default="output",
    )

    debug_args = parser.add_argument_group(title="Debug")
    debug_args.add_argument(
        "--version",
        action="store_true",
        help="print the tool version and exit",
    )
    debug_args.add_argument(
        "--debug",
        action="store_true",
        help="enable debug output",
    )

    args = parser.parse_args()

    # Print the current tool version and exit
    if args.version:
        sys.exit(print(f"BridgeKeeper - v{__version__}"))

    # Handle required argument conditions
    if not args.company and not args.names:
        parser.error("one of the arguments -c/--company -F/--file is required")

    if not args.format and not args.api:
        parser.error("one of the arguments -f/--format -a/--api is required")

    # If API is set, require a domain name
    if args.api and not args.domain:
        parser.error("both of the arguments -a/--api and -d/--domain are required for Hunter.io")  # fmt: skip

    return args


def update_args(args: argparse.Namespace) -> argparse.Namespace:
    """Update command line arguments based on user input

    Arguments:
        args: argument namespace

    Returns:
        updates argument namespace
    """
    if args.names:
        if check_file(args.names):
            logging.debug(f"Loading names from: {args.names}")
            args.names = file_to_list(args.names)

        else:
            logging.debug(f"Names file not found, assuming comma delimited list")
            args.names = args.names.split(",")

    if args.bing_cookies:
        if check_file(args.bing_cookies):
            logging.debug(f"Loading Bing cookies from: {args.bing_cookies}")
            args.bing_cookies = cookie_file_to_dict(args.bing_cookies)

        else:
            logging.debug(f"Bing cookie file not found, assuming comma delimited list")
            args.bing_cookies = cookie_str_to_dict(args.bing_cookies)

    if args.google_cookies:
        if check_file(args.google_cookies):
            logging.debug(f"Loading Google cookies from: {args.google_cookies}")
            args.google_cookies = cookie_file_to_dict(args.google_cookies)

        else:
            logging.debug(f"Google cookie file not found, assuming comma delimited list")  # fmt: skip
            args.google_cookies = cookie_str_to_dict(args.google_cookies)

    if args.yahoo_cookies:
        if check_file(args.yahoo_cookies):
            logging.debug(f"Loading Yahoo cookies from: {args.yahoo_cookies}")
            args.yahoo_cookies = cookie_file_to_dict(args.yahoo_cookies)

        else:
            logging.debug(f"Yahoo cookie file not found, assuming comma delimited list")  # fmt: skip
            args.yahoo_cookies = cookie_str_to_dict(args.yahoo_cookies)

    return args


def main():
    """Entry point of BridgeKeeper."""

    args = parse_args()
    init_logger(args.debug)

    print(__banner__)
    args = update_args(args)

    # Track execution time
    start = time.time()

    # Create the output directory if not exists
    output_dir = args.output.strip("/")
    if not Path(output_dir).is_dir():
        logging.info(f"Creating output directory: {output_dir}")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Handle scraping for usernames
    if args.company:
        logging.info("Scraping search engines for user names")

        scraped_names = scrape(
            company=args.company,
            output_dir=output_dir,
            depth=args.depth,
            timeout=args.timeout,
            proxy=args.proxy,
            bing_cookies=args.bing_cookies,
            google_cookies=args.google_cookies,
            yahoo_cookies=args.yahoo_cookies,
        )

        if not scraped_names:
            logging.error("No user names were found")
            sys.exit(0)

        logging.info(f"Names found via search engine(s): {len(scraped_names)}")

        names = scraped_names

    # If name file provided, load names
    else:
        names = args.names

        logging.info(f"Names loaded: {len(names)}")

    # Handle scraping Hunter.io
    if args.api and args.domain:
        logging.info("Hunting Hunter.io for emails and username format")

        (hunterio_emails, hunterio_format) = hunt(
            domain=args.domain,
            api_key=args.api,
            timeout=args.timeout,
            proxy=args.proxy,
        )

        if not hunterio_format:
            logging.error("No username format found")
            sys.exit(0)

        logging.info(f"Username format found via Hunter.io: {hunterio_format}")
        logging.info(f"Emails found via Hunter.io: {len(hunterio_emails)}")

        username_format = hunterio_format

    # If username format(s) provided, load format(s)
    else:
        username_format = args.format
        logging.info(f"Username format(s): {username_format}")

    logging.info("Transforming names")

    # Convert names to upper/lower, if specified
    if args.upper or args.lower:
        names = (
            [name.lower() for name in names]
            if args.lower
            else [name.upper() for name in names]
        )

    # Transform found names to email addresses
    # Return a mapping of username format template -> formatted usernames
    formatted_usernames = transform(username_format, names)

    # If we used Hunter.io, add uniquely scraped emails since they should
    # already be in the correct username/email format
    if args.api and args.domain:
        formatted_usernames[username_format] = formatted_usernames[username_format] | set(hunterio_emails)  # fmt: skip

    unique_usernames = sum(len(formatted_usernames[t]) for t in formatted_usernames)
    logging.info(f"Number of unique usernames found: {unique_usernames}")

    # Write converted usernames to output directory
    if any(len(formatted_usernames[t]) > 0 for t in formatted_usernames.keys()):
        logging.info(f"Writing usernames to the following directory: {output_dir}")

        company_fname = ""
        if args.company:
            company_fname = args.company.replace(".", "_").replace(" ", "-") + "_"

        # Loop over format templates
        for template in formatted_usernames.keys():
            template_fname = template.replace("{", "").replace("}", "")
            template_outfile = f"{output_dir}/{company_fname}{template_fname}_{START_SCRIPT}.txt"  # fmt: skip

            logging.debug(f"Writing '{template}' to: {template_outfile}")
            with open(template_outfile, "w") as f:
                for username in formatted_usernames[template]:
                    f.write(f"{username}\n")

    elapsed = time.time() - start
    logging.debug(f"{__file__} executed in {elapsed:.4f} seconds.")


if __name__ == "__main__":
    main()
