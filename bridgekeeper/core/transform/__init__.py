#!/usr/bin/env python3

import logging
import re
from typing import (
    Dict,
    List,
)

from bridgekeeper.core.transform.transformer import Transformer


def transform(
    format_: str,
    names: List[str],
) -> Dict[str, set]:
    """Convert a list of names to provided username format(s).

    Arguments:
        format_: format(s) to transform names (comma delimited)
        names: list of names to transform

    Returns:
        dictionary of username templates -> list of transformed usernames
    """
    transformer = Transformer()

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
            logging.error(f"Invalid username format: '{template}'")
            usernames.pop(template, None)

        else:
            logging.debug(f"Formatting names: '{template}'")

            for name in names:
                # Account for blank names
                name = name.strip()
                if not name:
                    continue

                try:
                    # Pass in the name and format template to perform name
                    # transformation. Pass in the current list of transformed
                    # names for the current template to identify duplicates so
                    # we can append counters (i.e. JSmith -> JSmith1)
                    usernames[template].add(
                        transformer.transform(name, template, usernames[template])
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
                                transformer.transform(
                                    f"{first_name} {l_name}",
                                    template,
                                    usernames[template],
                                )
                            )

                except Exception as e:
                    logging.error(f"Error when attempting to transform: {name}")
                    logging.debug(f"{e}")
                    pass

    return usernames
