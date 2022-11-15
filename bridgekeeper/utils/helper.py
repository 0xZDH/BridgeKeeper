#!/usr/bin/env python3

from pathlib import Path
from typing import Dict


def check_file(f: str) -> bool:
    """Check if a file exists

    Arguments:
        f: file name

    Returns:
        boolean if the file exists
    """
    try:
        if Path(f).is_file():
            return True

        return False

    # Handle errors like 'File name too long' in the case
    # of multiple names or cookies provided in place of a
    # file name
    except:
        return False


def cookie_file_to_dict(cookie_file: str) -> Dict[str, str]:
    """Read in a cookie file and parse to a dictionary

    Arguments:
        cookie_file: name of file containing cookies

    Returns:
        dictionary of parsed cookies
    """
    cookies = {}
    cookies_ = [x.strip() for x in open(cookie_file).readlines()]
    for c in cookies_:
        tmp_cookies = cookie_str_to_dict(c)
        cookies = {**cookies, **tmp_cookies}

    return cookies


def cookie_str_to_dict(cookie: str) -> Dict[str, str]:
    """Read in a cookie string and parse to a dictionary

    Arguments:
        cookie: cookie string

    Returns:
        dictionary of parsed cookie(s)
    """
    cookies = {}
    for c in cookie.split(";"):
        if c:
            c = c.strip()
            try:
                name, value = c.split("=", 1)
                cookies[name] = value

            except:
                pass

    return cookies
