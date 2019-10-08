#!/usr/bin/env python3

import re
import time
import argparse
from core.scraper import Scraper
from core.transformer import Transformer


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Scrape employee names from search engine LinkedIn profiles. Convert employee names to a specified username format.")

    # Allow a user to scrape names or just convert an already generated list of names
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-c", "--company", type=str, help="Target company to search for LinkedIn profiles.")
    group.add_argument("-F", "--file",    type=str, help="File containing names to be converted to usernames. Name format: 'First Last'")

    parser.add_argument("-f", "--format",  type=str, help="Specify username format. Valid format identifiers: {first}, {middle}, {last}, {f}, {m}, {l}, [#] (For trimming names)")
    parser.add_argument("-d", "--depth",   type=int, help="Number of pages to search each search engine. Default: 5", default=5)
    parser.add_argument("-t", "--timeout", type=int, help="Specify request timeout. Default: 25", default=25)
    parser.add_argument("-o", "--output",  type=str, help="Directory to write username files to.")
    parser.add_argument("--proxy",         type=str, help="Proxy to pass traffic through: <ip:port>")
    parser.add_argument("--lower",         action="store_true", help="Force usernames to all lower case.")
    parser.add_argument("--upper",         action="store_true", help="Force usernames to all upper case.")
    parser.add_argument("--debug",         action="store_true", help="Enable debug output.")
    args = parser.parse_args()

    start = time.time()

    if args.company:
        scraper = Scraper(args.company, depth=args.depth, timeout=args.timeout, proxy=args.proxy)
        scraper.loop.run_until_complete(scraper.run())
        print("\n[+] Names Found: %d" % len(scraper.employees))

    if args.format:
        print("[*] Converting found names to: %s" % args.format)
        transform = Transformer(args.debug)
        usernames = {f.strip(): [] for f in args.format.split(',')}
        for template in usernames.keys():
            if any(t[1:-1] not in ["first","middle","last",'f','m','l'] for t in re.findall(r'\{.+?\}', template)):
                print("[!] Invalid username format: %s" % (template))
                usernames.pop(template, None) # Remove invalid template

            else:
                names = scraper.employees if args.company else open(args.file, 'r').readlines()
                if args.upper or args.lower:
                    names = [name.lower() for name in names] if args.lower else [name.upper() for name in names]

                for name in names:
                    usernames[template].append(transform.transform(name, template, usernames[template]))
                    # Handle hyphenated last names
                    if '-' in name:
                        name = name.split()
                        nm   = ' '.join(n for n in name[:-1])
                        for ln in name[-1].split('-'):
                            _nm = "%s %s" % (nm, ln)
                            usernames[template].append(transform.transform(_nm, template, usernames[template]))

    output = args.output if args.output else "./"
    if args.debug: print("[DEBUG] Writing names and usernames to files in the following directory: %s" % output)

    if args.company:
        with open("%s/names.txt" % (output), 'a') as f:
            for name in scraper.employees:
                f.write("%s\n" % name)

    if args.format:
        for template in usernames.keys():
            with open("%s/%s.txt" % (output, template.replace('{','').replace('}','')), 'w') as f:
                for username in usernames[template]:
                        f.write("%s\n" % username)


    elapsed = time.time() - start
    if args.debug: print("\n[DEBUG] %s executed in %0.4f seconds." % (__file__, elapsed))