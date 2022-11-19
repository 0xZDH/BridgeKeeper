#!/usr/bin/env python3

import string
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
)


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


def file_to_list(f: str) -> List[Any]:
    """Read a file's lines into a list.

    Arguments:
        f: file to read into a list

    Returns:
        list of file lines
    """
    with open(f, "r") as f:
        list_ = [l.strip() for l in f if l.strip() not in [None, ""]]

    return list_


def check_substring(s: str, sub: str) -> bool:
    """Check if a substring exists within a given string
    Ignore punctuations and whitespace (except spaces)

    Arguments:
        s: primary string
        sub: substring

    Returns:
        if the translated substring exists in the string
    """
    # Force consistent casing
    s = s.lower()
    sub = sub.lower()

    # Build the character set to remove
    remove_char_set = string.punctuation + string.whitespace
    remove_char_set = remove_char_set.replace(" ", "")  # Remove spaces

    # Create translation tables
    s_table = s.maketrans(dict.fromkeys(remove_char_set))
    sub_table = sub.maketrans(dict.fromkeys(remove_char_set))

    return sub.translate(sub_table) in s.translate(s_table)
