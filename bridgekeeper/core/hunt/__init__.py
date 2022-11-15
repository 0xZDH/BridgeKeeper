#!/usr/bin/env python3

import logging
from typing import (
    Set,
    Tuple,
)

from bridgekeeper.core.hunt.hunter import Hunter


def hunt(
    domain: str,
    api_key: str,
    timeout: float = 25,
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
        (found emails, email format)
    """
    hunter = Hunter(
        domain=domain,
        api_key=api_key,
        timeout=timeout,
        proxy=proxy,
    )

    # Hunt format and emails
    username_format = hunter.hunt_format()
    found_emails = hunter.hunt_emails()

    return (found_emails, username_format)
