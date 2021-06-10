#!/usr/bin/env python3

import re
import time
import logging
import urllib3
import argparse
from typing import Tuple, Dict, List, Set
from pathlib import Path
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from core import (  # type: ignore
    Hunter,
    Scraper,
    Transformer,
)

_V_MAJ = 0
_V_MIN = 2
_V_MNT = 0
START_SCRIPT = datetime.now().strftime("%Y%m%d%H%M")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        populated namespace

    Raises:
        argument parser error when required args missing
    """
    parser = argparse.ArgumentParser(
        description=f"BridgeKeeper - v{_V_MAJ}.{_V_MIN}.{_V_MNT}"
    )

    # Allow a user to scrape names or just convert an already generated list of names
    usr_group = parser.add_mutually_exclusive_group(required=True)
    usr_group.add_argument(
        "-c",
        "--company",
        type=str,
        help="Target company to search for LinkedIn profiles (e.g. 'Example Ltd.').",
    )
    usr_group.add_argument(
        "--file",
        type=str,
        help="File containing names to be converted to usernames. Name format: 'First Last'",
    )

    # Require a user to specify whether to pull a username format from Hunter.io
    # or specify a format manually
    fmt_group = parser.add_mutually_exclusive_group(required=True)
    fmt_group.add_argument("-a", "--api", type=str, help="Hunter.io API key.")
    fmt_group.add_argument(
        "-f",
        "--format",
        type=str,
        help=(
            "Specify username format. "
            "Valid format identifiers: {first}, {middle}, {last}, {f}, {m}, {l}, [#]"
        ),
    )

    # Remaining arguments
    parser.add_argument(
        "--domain",
        type=str,
        help=(
            "Domain name of target company for Hunter.io email format "
            "identification and email scraping."
        ),
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        help="Number of pages deep to search each search engine. Default: 5",
        default=5,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        help="HTTP request timeout in seconds. Default: 25 seconds",
        default=25,
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Directory to write output files to. Default: ./output/",
        default="output",
    )
    parser.add_argument(
        "--cookie", type=str, help="File containing Google CAPTCHA bypass cookies."
    )
    parser.add_argument(
        "--proxy", type=str, help="Proxy to pass HTTP traffic through: `Host:Port`"
    )
    parser.add_argument(
        "--lower", action="store_true", help="Force usernames to all lower case."
    )
    parser.add_argument(
        "--upper", action="store_true", help="Force usernames to all upper case."
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    # Handle argument conditions
    if args.api and not args.domain:
        parser.error("--domain required when using -a/--api for Hunter.io.")

    return args


def scrape(
    company: str,
    output_dir: str,
    depth: int = 5,
    timeout: int = 25,
    proxy: str = None,
    cookie: str = None,
) -> Scraper:  # type: ignore
    """Scrape Google, Bing, and Yahoo for LinkedIn profiles by
    invoking the Scraper module. Write found names to a file
    in a designated output directory.

    Arguments:
        company: name of company to scrape (i.e. 'Example Ltd.')
        output_dir: directory where to write names file to
        depth: number of pages deep to scrape per search engine
        timeout: request timeout (HTTP)
        proxy: request proxy (HTTP)
        cookie: file name containing Google CAPTCHA bypass cookie(s)

    Returns:
        (scraper, output file)
    """
    scraper = Scraper(  # type: ignore
        company,
        depth=depth,
        timeout=timeout,
        proxy=proxy,
        cookies=cookie,
    )
    scraper.loop.run_until_complete(scraper.run())

    # Create file to write users to: <example_ltd>_names_<date>.txt
    company = company.strip().strip(".")
    company_fname = company.replace(".", "_").replace(" ", "_")
    output_file = f"{output_dir}/{company_fname}_names_{START_SCRIPT}.txt"

    logging.info(f"LinkedIn Names Found: {len(scraper.employees)}")
    logging.info(f"Writing names to the following file: {output_file}")

    with open(output_file, "a") as f:
        for name in scraper.employees:
            f.write(f"{name}\n")

    return scraper


def hunt(
    domain: str,
    api_key: str,
    timeout: str = 25,
    proxy: str = None,
) -> Tuple[Set[str], str]:
    """Run Hunter.io to get a username format for the target domain
    as well as any available email addresses -> These should already
    be in the correct username format.

    Arguments:
        domain: domain name to search within Hunter.io
        api_key: Hunter.io API key
        timeout: request timeout (HTTP)
        proxy: request proxy (HTTP)

    Returns:
        (username format, hunter)
    """
    hunter = Hunter(  # type: ignore
        domain,
        api_key=api_key,
        timeout=timeout,
        proxy=proxy,
    )

    # Hunt format and emails
    format_ = hunter.hunt_format()
    emails = hunter.hunt_emails()

    logging.info(f"Hunter.io Format Identified: {format_}")
    logging.info(f"Hunter.io Emails Found: {len(emails)}")

    return (emails, format_)


def transform_names(
    format_: str,
    names: List[str],
) -> Dict[str, set]:  # type: ignore
    """Convert a list of names to provided username format(s).

    Arguments:
        format_: format(s) to transform names to usernames
        names: list of names to transform

    Returns:
        dictionary of username templates -> list of converted usernames
    """
    transform = Transformer()  # type: ignore

    # Create a username template map: format -> empty set
    usernames = {f.strip(): set() for f in format_.split(",")}

    # Loop over each username format template and transform each
    # name
    valid_formatters = ["first", "middle", "last", "f", "m", "l"]
    for template in usernames.keys():
        # Check if any of the formatters in the current template
        # are invalid. If invalid, pop from list
        # Find all text within formatter identifiers: {...}
        found_formatters = re.findall(r"\{(.+?)\}", template)
        if any(fmt not in valid_formatters for fmt in found_formatters):
            logging.error(f"Invalid username format: {template}")
            usernames.pop(template, None)
        else:
            for name in names:
                try:
                    # Pass in the name and format template to perform name
                    # transformation. Pass in the current list of transformed
                    # names for the current template to identify duplicates so
                    # we can append counters (i.e. JSmith -> JSmith1)
                    usernames[template].add(
                        transform.transform(name, template, usernames[template])
                    )

                    # Handle hyphenated last names. Split the full name on spaces,
                    # so we isolate the last name and split on hyphens. Then, run
                    # the full name with all variations of last name (i.e. if the
                    # last name is Smith-Adams, we transform Smith, Adams,
                    # Smith-Adams, and SmithAdams)
                    if "-" in name:
                        split_name = name.split()

                        first_name = " ".join(split_name[:-1])
                        last_name = split_name[-1]

                        # Join split last names with fully hyphenated last name
                        last_names = last_name.split("-") + [
                            last_name,
                            last_name.replace("-", ""),
                        ]
                        for l_name in last_names:
                            usernames[template].add(
                                transform.transform(
                                    f"{first_name} {l_name}",
                                    template,
                                    usernames[template],
                                )
                            )
                except Exception as e:
                    logging.error(f"Error when attempting to transform: {name}")
                    pass

    return usernames


def main():
    """Entry point of BridgeKeeper."""

    # Parse command line arguments
    args = parse_args()

    # Initialize logging level and format
    if args.debug:
        logging_format = (
            "[%(asctime)s] %(levelname)-5s - %(filename)17s:%(lineno)-4s - %(message)s"
        )
        logging_level = logging.DEBUG
    else:
        logging_format = "[%(asctime)s] %(levelname)-5s: %(message)s"
        logging_level = logging.INFO

    logging.basicConfig(format=logging_format, level=logging_level)
    logging.addLevelName(logging.WARNING, "WARN")

    # Track execution time
    start = time.time()

    # Create the output directory if not exists
    current_directory = Path(__file__).parent.absolute()
    output_directory = args.output.strip("/")
    Path(f"{current_directory}/{output_directory}").mkdir(parents=True, exist_ok=True)
    output = f"{current_directory}/{output_directory}"

    # Handle scraping for usernames
    if args.company:
        logging.info("Scraping search engines for usernames")
        scraper = scrape(
            args.company,
            output,
            int(args.depth),
            int(args.timeout),
            args.proxy,
            args.cookie,
        )

    # Only get format from Hunter.io if API key and domain are set
    if args.api and args.domain:
        logging.info("Hunting Hunter.io for emails and username format")
        (emails, format_) = hunt(
            args.domain,
            args.api,
            int(args.timeout),
            args.proxy,
        )
        if not format_:
            raise ValueError("No username format identified.")
    else:
        format_ = args.format
        logging.info(f"Using username format: {format_}")

    # Create a list of names to work with based on whether we collected names
    # via scraping or a provided file
    names = scraper.employees if args.company else open(args.file, "r").readlines()

    # Convert names to upper/lower if specified
    if args.upper or args.lower:
        names = (
            [name.lower() for name in names]
            if args.lower
            else [name.upper() for name in names]
        )

    usernames = transform_names(format_, names)

    # If we used Hunter.io -> Add scraped emails since they should already be in
    # the correct username format
    if args.api and args.domain:
        usernames[format_] = usernames[format_] | set(emails)

    logging.info(
        "Number of unique usernames identified: %d"
        % sum(len(usernames[t]) for t in usernames.keys())
    )

    # Write converted usernames to output directory
    if any(len(usernames[t]) > 0 for t in usernames.keys()):
        logging.info(f"Writing usernames to the following directory: {output}")

        company_fname = ""
        if args.company:
            company_fname = args.company.replace(".", "_").replace(" ", "_") + "_"

        for template in usernames.keys():
            template_fname = template.replace("{", "").replace("}", "")
            output_file = f"{output}/{company_fname}{template_fname}_{START_SCRIPT}.txt"

            with open(output_file, "w") as f:
                for username in usernames[template]:
                    f.write(f"{username}\n")

    elapsed = time.time() - start
    logging.debug(f"{__file__} executed in {elapsed:.4f} seconds.")


if __name__ == "__main__":
    main()
