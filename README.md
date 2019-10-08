# BridgeKeeper

<p align="center"><img src="https://media.giphy.com/media/e9aSISpSTtU4w/giphy.gif"></p>

Scrape employee names from search engine LinkedIn profiles. Convert employee names to a specified username format.

### Usage

```
usage: bridgekeeper.py [-h] (-c COMPANY | -F FILE) [-f FORMAT] [-d DEPTH]
                       [-t TIMEOUT] [-o OUTPUT] [--proxy PROXY] [--lower]
                       [--upper] [--debug]

Scrape employee names from search engine LinkedIn profiles. Convert employee names to a specified username format.

optional arguments:
  -h, --help            show this help message and exit
  -c COMPANY, --company COMPANY
                        Target company to search for LinkedIn profiles.
  -F FILE, --file FILE  File containing names to be converted to usernames.
                        Name format: 'First Last'
  -f FORMAT, --format FORMAT
                        Specify username format. Valid format identifiers:
                        {first}, {middle}, {last}, {f}, {m}, {l}, [#] (For
                        trimming names)
  -d DEPTH, --depth DEPTH
                        Number of pages to search each search engine. Default:
                        5
  -t TIMEOUT, --timeout TIMEOUT
                        Specify request timeout. Default: 25
  -o OUTPUT, --output OUTPUT
                        Directory to write username files to.
  --proxy PROXY         Proxy to pass traffic through: <ip:port>
  --lower               Force usernames to all lower case.
  --upper               Force usernames to all upper case.
  --debug               Enable debug output.
```

### Examples

Gather employee names for a company, Example, and convert each name into an 'flast' username formatted email:<br>
`$ python3 bridgekeeper.py --company example --format {f}{last}@example.com --depth 10 --proxy 127.0.0.1:8080 --output example-employees/ --debug`

Convert an already generated list of names to usernames:<br>
`$ python3 bridgekeeper.py --file names.txt --format {f}{last}@example.com --output example-employees/ --debug`


Username format examples (BridgeKeeper supports middle names as well as character limited usernames - e.g. only 4 characters of a last name is used):<br>
```
Name: John Adams Smith
{f}{last}                   > jsmith
{f}{m}.{last}               > ja.smith
{f}{last}[4]@example.com    > jsmit@example.com
```

### Features

* Support for all three major search engines: Google, Bing, and Yahoo
* Name parsing to strip LinkedIn titles, certs, prefixes, etc.
* Username formatting with support for trickier username formats
  * i.e. If a username format has only the first 4 characters of the last name
* Search engine blacklist evasion
* Proxying
* Hyphenated last name handling
* Duplicate username handling
  * Incrementing numbers appended to duplicate usernames

### TODO

* Add flag to call Pymeta/Pymeta clone

### Acknowledgements

**m8r0wn** - [CrossLinked](https://github.com/m8r0wn/CrossLinked)