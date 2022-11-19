#!/usr/bin/env python3

import logging
import re
from typing import (
    List,
    Tuple,
)


class Transformer(object):
    """Convert names into various username formats."""

    def __duplicate(
        self,
        username: str,
        list_: List[str],
        count: int = 1,
    ) -> str:
        """Handle duplicate usernames by appending an incrementing
        integer value.

        Arguments:
            username: username to check against list for duplicates
            list_: list of current usernames to check against
            count: current duplicate count

        Returns:
            username with duplicate count appended
        """
        dup = f"{username}{(count)}"
        return (
            self.__duplicate(username, list_, count=(count + 1))
            if dup in list_
            else dup
        )

    def __trim(
        self,
        f: str,
        m: str,
        l: str,
        template: str,
        delim: str = "{",
    ) -> Tuple[str, str, str]:
        """Trim a predefined portion of a name by based on a
        username template.

        Arguments:
            f: first name string
            m: middle name string
            l: last name string
            template: username format template
            delim: format delimeter

        Returns:
            trimmed f/m/l names based on format template
        """
        # Loop over each formatter in username template (i.e. {f}, {m}, etc.)
        # We split on the defined delimeter and then reconstruct the formatters
        # by adding the delimeter back
        for item in [(delim + e) for e in template.split(delim) if e]:
            # Check if the user specified a length for the current formatter
            # Look for: `}[#]`
            if re.search("}\[[-]?[0-9]+\]", item):
                # Grab the trim number: int within [...]
                trim = int(re.search("\[([-]?[0-9]+)\]", item).group(1))

                # Grab the formatter to be trimmed: string within {...}
                fmt = re.search("\{(.+)\}", item).group(1)

                # Trim the data accordingly
                if fmt in ["first", "f"]:
                    f = f[:trim]

                elif fmt in ["middle", "m"]:
                    m = m[:trim]

                elif fmt in ["last", "l"]:
                    l = l[:trim]

        return (f, m, l)

    def transform(
        self,
        name: str,
        template: str,
        list_: List[str] = None,
    ) -> str:
        """Transform name using a given username format template.

        Arguments:
            name: name for transform
            template: username format template
            list_: list of current transformed names

        Returns:
            transformed name

        Excepts:
            KeyError: if f/m/l can't be accessed, return an empty
              username string
        """
        # Split the name into section (f/m/l)
        name = name.strip().split()
        (f, l) = (name[0], name[-1])
        m = name[1] if len(name) > 2 else ""

        # Check if the format specifies to trim a given section
        # of the name
        if re.search("\[[-]?[0-9]+\]", template):
            (f, m, l) = self.__trim(f, m, l, template)

        try:
            username = template.format(
                first=f, middle=m, last=l, f=f[:1], m=m[:1], l=l[:1]
            )
            # Remove trim identifier from username
            username = re.sub("\[[-]?[0-9]+\]", "", username)

            # Check and handle duplicates by appending a duplicate
            # counter
            if list_ and username in list_:
                username = self.__duplicate(username, list_)

        except KeyError as e:
            logging.debug(f"{e}")
            username = ""

        return username
