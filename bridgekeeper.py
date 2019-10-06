#!/usr/bin/env python

import re
import sys
import time
import argparse

"""Convert names into various username formats."""

class Transform:

    # Predefined username formats
    predefined = {} # {Transform Name: [Transformed Username, ...]}
    templates  = ["{first}.{last}",  # First.Last
                  "{first}_{last}",  # First_Last
                  "{first}-{last}",  # First-Last
                  "{first}.{l}",     # First.L
                  "{first}_{l}",     # First_L
                  "{first}-{l}",     # First-L
                  "{f}.{last}",      # F.Last
                  "{f}_{last}",      # F_Last
                  "{f}-{last}",      # F-Last
                  "{f}{last}",       # FLast
                  "{first}{l}",      # FirstL
                  "{first}",         # First
                  "{f}{l}",          # FL

                  "{last}.{first}",  # Last.First
                  "{last}_{first}",  # Last_First
                  "{last}-{first}",  # Last-First
                  "{last}.{f}",      # Last.F
                  "{last}_{f}",      # Last_F
                  "{last}-{f}",      # Last-F
                  "{l}.{first}",     # L.First
                  "{l}_{first}",     # L_First
                  "{l}-{first}",     # L-First
                  "{l}{first}",      # LFirst
                  "{last}{f}",       # LastF
                  "{last}",          # Last
                  "{l}{f}"]          # LF


    def __init__(self, debug=False):
        self.__debug = debug
        for t in self.templates:
            self.predefined[t] = []


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

        if re.search("\[([-]?[0-9]+)\]", template):
            (f, m, l) = self.__trim(f, m, l, template)

        try:
            username = template.format(first=f, middle=m, last=l, f=f[:1], m=m[:1], l=l[:1])
            username = re.sub("\[([-]?[0-9]+)\]", "", username)
            if _list and username in _list:
                username = self.__duplicate(username, _list)

        except KeyError as e:
            if self.__debug: print("[DEBUG] %s" % e)
            username = ""

        return username



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert name to username format.")
    parser.add_argument("-l", "--list",   action="store_true", help="List predefined username formats.")
    parser.add_argument("-a", "--all",    action="store_true", help="Convert using all predefined username formats.")
    parser.add_argument("-f", "--format", type=str, help="Specify predefined or custom username format. Valid format identifiers: {first}, {middle}, {last}, {f}, {m}, {l}")
    parser.add_argument("-F", "--file",   type=str, help="File containing names formatted as 'First Last'.")
    parser.add_argument("-n", "--name",   type=str, help="Single/List of names formatted as 'First Last' delimited by a comma (,).")
    parser.add_argument("-o", "--output", type=str, help="Directory to write username files to.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output.")
    parser.add_argument("--lower", action="store_true", help="Force usernames to all lower case.")
    parser.add_argument("--upper", action="store_true", help="Force usernames to all upper case.")

    args = parser.parse_args()

    start = time.time()

    transform = Transform(args.debug)

    # List all predefined transforms
    if args.list:
        print("[ + ] List of predefined templates:")
        for t in transform.templates:
            print("      > %s" % t)

    # Handle name tranformation
    else:
        # Handle parser errors
        if not args.file and not args.name:
            parser.error("-F/--file or -n/--name required with the selected options.")

        if not args.all and not args.format:
            parser.error("-a/--all or -f/--format required with the selected options.")

        names = [n.strip() for n in open(args.file, "r").readlines() if n.strip() not in ("", None)] if args.file else args.name.split(',')

        # Handle forced upper/lower case (default to lower)
        if args.upper or args.lower:
          names = [name.lower() for name in names] if args.lower else [name.upper() for name in names]

        if args.all:
            usernames = transform.predefined
            for template in transform.templates:
                for name in names:
                    usernames[template].append(transform.transform(name, template, usernames[template]))

        else:
            # Make sure there is no invalid format identifiers
            if any(x[1:-1] not in ["first","middle","last",'f','m','l'] for x in re.findall(r'\{.+?\}', args.format)):
                print("[!] Invalid format: %s" % (args.format))
                print("[*] Valid format identifiers: {first}, {middle}, {last}, {f}, {m}, {l}")
                sys.exit(1)

            usernames = {args.format: []}
            for name in names:
                usernames[args.format].append(transform.transform(name, args.format, usernames[args.format]))

        if not args.output:
            print(usernames)

        else:
            for template in usernames.keys():
                with open("%s/%s.txt" % (output, t.replace('{','').replace('}','')), 'w') as f:
                    for username in usernames[template]:
                        f.write("%s\n" % username)

    elapsed = time.time() - start
    if args.debug: print("\n[DEBUG] %s executed in %0.4f seconds." % (__file__, elapsed))
