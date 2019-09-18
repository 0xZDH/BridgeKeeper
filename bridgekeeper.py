#!/usr/bin/env python

"""Transform names into different username formats."""

import os
import sys
import errno
import argparse
from string import Template


# Predefined username formats
f0 = Template("${first}.${last}")     # First.Last
f1 = Template("${first}.${l}")        # First.L
f2 = Template("${f}.${last}")         # F.Last
f3 = Template("${first}_${last}")     # First_Last
f4 = Template("${first}_${l}")        # First_L
f5 = Template("${f}_${last}")         # F_Last
f6 = Template("${f}${last}")          # FLast
f7 = Template("${first}${l}")         # FirstL
f8 = Template("${first}")             # First

l0 = Template("${last}.${first}")     # Last.First
l1 = Template("${last}.${f}")         # Last.F
l2 = Template("${l}.${first}")        # L.First
l3 = Template("${last}_${first}")     # Last_First
l4 = Template("${last}_${f}")         # Last_F
l5 = Template("${l}_${first}")        # L_First
l6 = Template("${last}${f}")          # LastF
l7 = Template("${l}${first}")         # LFirst
l8 = Template("${last}")              # Last

t_list = [f0,f1,f2,f3,f4,f5,f6,f7,f8,l0,l1,l2,l3,l4,l5,l6,l7,l8]


# Clean template for key names
def clean_template(t):
    return t.safe_substitute().replace("$","").replace("{","").replace("}","")


# Trim first or last name according to user input
def trim_name(name, count, trim):
    if not count and not trim:
        return (name[0], name[-1])

    else:
        if trim == "first":
            return (name[0][:count], name[-1])

        elif trim == "last":
            return (name[0], name[-1][:count])


# List all predefined transforms
def list_transforms():
    print("[ + ] List of transforms:")
    for transform in predefined.keys():
        print("      > %s" % transform.replace('x', '_'))


# Return an incrementing integer value to duplicate usernames
def handle_dup(type_, username, usernames, count=1):
    tmp = username + str(count + 1)
    if tmp in usernames[type_]:
        handle_dup(type_, username, usernames, count=(count + 1))

    else:
        return tmp


# Loop through names and transform them using all predefined transforms
def transform_predefined(names, format_=None, count=None, trim=None):
    if not format_:
        usernames = predefined
    else:
        usernames = {format_: []}

    for name in names:
        fullname = name.strip().split()
        (first, last) = trim_name(fullname, count, trim)

        for t in t_list:
            type_    = clean_template(t) # Transform template for key value
            username = t.substitute(first=first, last=last, f=first[0], l=last[0], x='_')

            if type_ in usernames.keys():
                if not username in usernames[type_]:
                    usernames[type_].append(username)

                else:
                    usernames[type_].append(handle_dup(type_, username, usernames))

    return usernames


# Loop through names and transform them using a user designed format
def transform_design(list_, format_, count=None, trim=None):
    template  = Template(format_)
    type_     = clean_template(template) # Transform template for key value
    usernames = {type_: []}
    for name in list_:
        fullname = name.strip().split()
        (first, last) = trim_name(fullname, count, trim)

        username = template.substitute(first=first, last=last, f=first[0], l=last[0], x='_')

        if not username in usernames[type_]:
            usernames[type_].append(username)

        else:
            usernames[type_].append(handle_dup(type_, username, usernames))

    return usernames


# Write transformed usernames to approriate files
def write_usernames(output, usernames):
    for type_ in usernames.keys():
        with open("%s/%s.txt" % (output, type_), 'w') as f:
            for item in usernames[type_]:
                f.write("%s\n" % item)



# Initialize a dictionary as a temporary holding for predefined transforms
predefined = {}
for t in t_list:
    predefined[clean_template(t)] = [] # Transform template for key value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Name transformer.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--list",   action="store_true", help="List all predefined username formats.")
    group.add_argument("-a", "--all",    action="store_true", help="Transform using all predefined username formats.")
    group.add_argument("-f", "--format", type=str, help="Transform using a specific predefined username format.")
    group.add_argument("-d", "--design", type=str, help="Design a custom username format to transform with. Format Examples: {first}{last}, {f}{last}[4]")

    parser.add_argument("-c", "--count",  type=int, help="How many characters to use from [First] or [Last] during transform.")
    parser.add_argument("-t", "--trim",   default=None, const="last", nargs='?', choices=["first", "last"], help="Trim [First] or [Last] during transform.")
    parser.add_argument("-n", "--names",  type=str, help="File containing names formatted as '[First] [Last]'.")
    parser.add_argument("-s", "--single", type=str, help="Single name formatted as '[First] [Last]'.")
    parser.add_argument("-o", "--output", type=str, help="Directory to write usernames to.")

    args = parser.parse_args()


    # Make sure a names file or single name instance was provided
    if not args.list and (not args.names and not args.single):
        parser.error("-n/--names or -s/--single required with the selected options.")


    # List all predefined transforms
    if args.list:
        list_transforms()

    # Handle name tranforms
    else:
        if (args.count and not args.trim) or (args.trim and not args.count):
            parser.error("-c/--count and -t/--trim must be used together or not at all.")

        names = [n for n in open(args.names, "r").readlines()] if args.names else [args.single]

        # Transform given name(s) using all predefined transforms
        if args.all:
            usernames = transform_predefined(names, count=args.count, trim=args.trim)
            if not args.output:
                print(usernames)

        # Transform given name(s) using a predefined transform
        elif args.format:
            if args.format not in predefined.keys():
                parser.error("Invalid format provided. Please refer to -l/--list.")

            usernames = transform_predefined(names, format_=args.format, count=args.count, trim=args.trim)
            if not args.output:
                print(usernames)

        # Transform given name(s) using a user designed transform
        elif args.design:
            format_   = args.design.format(first="${first}", last="${last}", f="${f}", l="${l}")
            usernames = transform_design(names, format_, count=args.count, trim=args.trim)
            if not args.output:
                print(usernames)

    if args.output:
        write_usernames(args.output, usernames)