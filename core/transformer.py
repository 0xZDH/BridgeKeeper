#!/usr/bin/env python3

import re
import sys
import time
import argparse

"""Convert names into various username formats."""

class Transformer:

    def __init__(self, debug=False):
        self.__debug = debug


    def __duplicate(self, username, _list, count=1):
        """ Handle duplicate usernames by appending an incrementing integer value """
        dup = "%s%d" % (username, (count + 1))
        return self.__duplicate(username, _list, count=(count + 1)) if dup in _list else dup


    def __trim(self, f, m, l, template, delim='{'):
        """ Grab a predefined portion of a name """
        for item in [(delim + e) for e in template.split(delim) if e]:
            # Check if use specifies length > Look for '}[#]'
            if re.search("}\[[-]?[0-9]+\]", item):
                trim = int(re.search("\[([-]?[0-9]+)\]", item).group(1))
                name = re.search("\{(.+)\}", item).group(1)

                if name in ["first", "f"]:
                    f = f[:trim]

                elif name in ["middle", "m"]:
                    m = m[:trim]

                elif name in ["last", "l"]:
                    l = l[:trim]

        return (f, m, l)


    def transform(self, name, template, _list=None):
        """ Transform name using a template """
        name   = name.strip().split()
        (f, l) = (name[0], name[-1])
        m      = name[1] if len(name) > 2 else ""

        if re.search("\[[-]?[0-9]+\]", template):
            (f, m, l) = self.__trim(f, m, l, template)

        try:
            username = template.format(first=f, middle=m, last=l, f=f[:1], m=m[:1], l=l[:1])
            username = re.sub("\[[-]?[0-9]+\]", "", username)
            if _list and username in _list:
                username = self.__duplicate(username, _list)

        except KeyError as e:
            if self.__debug: print("[DEBUG] %s" % e)
            username = ""

        return username