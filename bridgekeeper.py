#!/usr/bin/env python

import re
import argparse
from string import Template

"""Transform names into various username formats."""

class Transform:

    # Predefined username formats
    __transforms = {} # {Transform Name: Transform Template, ...}
    __predefined = {} # {Transform Name: [Transformed Usernames], ...}
    __templates  = [Template("${first}.${last}"),     # First.Last
                    Template("${first}_${last}"),     # First_Last
                    Template("${first}-${last}"),     # First-Last
                    Template("${first}.${l}"),        # First.L
                    Template("${first}_${l}"),        # First_L
                    Template("${first}-${l}"),        # First-L
                    Template("${f}.${last}"),         # F.Last
                    Template("${f}_${last}"),         # F_Last
                    Template("${f}-${last}"),         # F-Last
                    Template("${f}${last}"),          # FLast
                    Template("${first}${l}"),         # FirstL
                    Template("${first}"),             # First
                    Template("${f}${l}"),             # FL

                    Template("${last}.${first}"),     # Last.First
                    Template("${last}_${first}"),     # Last_First
                    Template("${last}-${first}"),     # Last-First
                    Template("${last}.${f}"),         # Last.F
                    Template("${last}_${f}"),         # Last_F
                    Template("${last}-${f}"),         # Last-F
                    Template("${l}.${first}"),        # L.First
                    Template("${l}_${first}"),        # L_First
                    Template("${l}-${first}"),        # L-First
                    Template("${l}${first}"),         # LFirst
                    Template("${last}${f}"),          # LastF
                    Template("${last}"),              # Last
                    Template("${l}${f}")]             # LF


    def __init__(self):
        for t in self.__templates:
            self.__transforms[self.__clean_template(t)] = t  # Dictionary to identify transforms for use
            self.__predefined[self.__clean_template(t)] = [] # Dictionary as a temporary holding for predefined transforms


    # Clean templates for regular use
    def __clean_template(self, template):
        return template.safe_substitute().replace("$","").replace("{","").replace("}","")


    # Parse list of names into nested list of names i.e. [["First", "Middle", "Last"], [...]]
    def __parse_names(self, _list):
        return [[s for s in n.split()] for n in _list]


    # Append an incrementing integer value to duplicate usernames
    def __duplicate(self, template, name, _list, count=1):
        tmp = name + str(count + 1)
        if tmp in _list[template]:
            return __duplicate(template, name, _list, count=(c + 1))

        else:
            return tmp


    # This is super janky and is temporary until I find a better method
    # Trim a user defined portion of a username
    def __trim(self, f, m, l, template):
        temp = template.safe_substitute()

        for item in temp.split('$'):
            if re.search("\[[0-9]\]", item):
                trim = int(re.search("\[[0-9]\]", item).group().strip('[').strip(']'))
                name = re.search("\{(.*?)\}", item).group(1)

                if name in ["first", "f"]:
                    f = f[:trim]

                elif name in ["last", "l"]:
                    l = l[:trim]

                elif name in ["middle", "m"]:
                    m = m[:trim]

        return (f, m, l)


    # Transform names using: all templates, a specified predefined template, or a user defined template
    def __transform(self, _list, template=None, design=None):
        if not design:
            t_list    = self.__transforms.values() if not template else [self.__transforms[template]]
            usernames = self.__predefined if not template else {template: []}

        else:
            t_list    = [Template(design)]
            usernames = {self.__clean_template(t_list[0]): []}

        for t in t_list:
            type_ = self.__clean_template(t)

            for n in _list:
                (f, m, l) = (n[0], "", n[-1])

                # Grab a middle name if there is one
                if len(n) > 2:
                    m = n[1]

                # Handle user defined trimming
                if design:
                    if re.search("\[[0-9]\]", type_):
                        (f, m, l) = self.__trim(f, m, l, t)

                username = t.substitute(first=f, middle=m, last=l, f=f[:1], m=m[:1], l=l[:1]) # TODO: Add predefined middle name supported templates
                username = re.sub("\[[0-9]\]", "", username)
                usernames[type_].append(self.__duplicate(type_, username, usernames)) if username in usernames[type_] else usernames[type_].append(username)

        return usernames


    # Return list of predefined transforms
    def get_transform_list(self):
        return self.__transforms.keys()


    # Write transformed usernames to approriate files
    def write_file(self, output, _list):
        for t in _list.keys():
            with open("%s/%s.txt" % (output, t), 'w') as f:
                for i in _list[t]:
                    f.write("%s\n" % i)


    # Call the proper transform method
    def transform(self, _list, _all=False, _format=None, _design=None):
        names = self.__parse_names(_list)

        if _all:
            return self.__transform(names)

        elif _format:
            if _format.lower() not in self.__transforms.keys():
                print("Invalid predefined format provided. Please refer to the transform list.")
                exit(1)

            return self.__transform(names, template=_format.lower())

        elif _design:
            design = _design.lower().format(first="${first}", middle="${middle}", last="${last}", f="${f}", m="${m}", l="${l}")
            return self.__transform(names, design=design)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Name transformer.")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--list",    action="store_true", help="List all predefined username formats.")
    group.add_argument("-a", "--all",     action="store_true", help="Transform using all predefined username formats.")
    group.add_argument("-f", "--format",  type=str, help="Transform using a specific predefined username format.")
    group.add_argument("-d", "--design",  type=str, help="Design a custom username format to transform with. Format Examples: {first}x{last}, {f}-{last}")
    parser.add_argument("-F", "--file",   type=str, help="File containing names formatted as 'First Last'.")
    parser.add_argument("-s", "--single", type=str, help="Single name formatted as 'First Last'.")
    parser.add_argument("-o", "--output", type=str, help="Directory to write username files to.")

    args = parser.parse_args()

    # Intialize transform class object
    transform = Transform()

    # List all predefined transforms
    if args.list:
        print("[ + ] List of transforms:")
        for t in transform.get_transform_list():
            print("      > %s" % t)

    # Handle name tranforms
    else:
        # Handle parser errors
        if not args.file and not args.single:
            parser.error("-n/--names or -s/--single required with the selected options.")

        # Convert names file or single name to list
        names = [n.strip() for n in open(args.file, "r").readlines() if n.strip() not in ("", None)] if args.file else [args.single]

        # Transform username based on user specified option
        if args.all:
            usernames = transform.transform(names, _all=True)

        elif args.format:
            usernames = transform.transform(names, _format=args.format.lower())

        elif args.design:
            usernames = transform.transform(names, _design=args.design)

        if not args.output:
            print(usernames)

        else:
            transform.write_file(args.output, usernames)
