# BridgeKeeper

<p align="center"><img src="https://media.giphy.com/media/e9aSISpSTtU4w/giphy.gif"></p>

Scrape employee names from search engine LinkedIn profiles.<br>
Hunt for emails and username format(s) via Hunter.io.<br>
Transform names to given username format(s).

## Usage

```
usage: bridgekeeper.py [-h] (-c COMPANY | --file FILE) (-a API | -f FORMAT)
                       [--domain DOMAIN] [-d DEPTH] [-t TIMEOUT] [-o OUTPUT]
                       [--cookie COOKIE] [--proxy PROXY] [--lower] [--upper]
                       [--debug]

BridgeKeeper - v0.2.0

optional arguments:
  -h, --help            show this help message and exit

  -c COMPANY, --company COMPANY
                        Target company to search for LinkedIn profiles
                        (e.g. 'Example Ltd.').

  --file FILE           File containing names to be converted to usernames.
                        Name format: 'First Last'

  -a API, --api API     Hunter.io API key.

  -f FORMAT, --format FORMAT
                        Specify username format. Valid format identifiers:
                        {first}, {middle}, {last}, {f}, {m}, {l}, [#]

  --domain DOMAIN       Domain name of target company for Hunter.io email format
                        identification and email scraping.

  -d DEPTH, --depth DEPTH
                        Number of pages deep to search each search engine.
                        Default: 5

  -t TIMEOUT, --timeout TIMEOUT
                        HTTP request timeout in seconds. Default: 25 seconds

  -o OUTPUT, --output OUTPUT
                        Directory to write output files to. Default: ./output/

  --cookie COOKIE       File containing Google CAPTCHA bypass cookies.

  --proxy PROXY         Proxy to pass HTTP traffic through: `Host:Port`

  --lower               Force usernames to all lower case.

  --upper               Force usernames to all upper case.

  --debug               Enable debug output.
```

### Examples

Gather employee names for a company, Example, and convert each name into an 'flast' username formatted email:<br>
`$ bridgekeeper.py --company "Example Ltd." --format {f}{last}@example.com --depth 10 --output example-employees/ --debug`

Gather employee names and email addresses from search engines and Hunter.io:<br>
`$ bridgekeeper.py --company "Example Ltd." --domain example.com --api {API_KEY} --depth 10 --output example-employees/ --debug`

Convert an already generated list of names to usernames:<br>
`$ bridgekeeper.py --file names.txt --format {f}{last}@example.com --output example-employees/ --debug`


Username format examples (BridgeKeeper supports middle names as well as character limited usernames - e.g. only 4 characters of a last name is used):<br>
```
Name: John Adams Smith
{f}{last}                   > jsmith
{f}{m}.{last}               > ja.smith
{f}{last}[4]@example.com    > jsmit@example.com
```

## Features

* Support for three major search engines: Google, Bing, and Yahoo
* Name parsing to strip LinkedIn titles, certs, prefixes, etc.
* Search engine blacklist evasion
* HTTP request proxying
* Username formatting with support for trickier username formats
  * Name trimming
    * e.g. If a username format has only the first 4 characters of the last name
  * Hyphenated last name handling
  * Duplicate username handling
    * Incrementing numbers appended to duplicate usernames
* Use Hunter.io to identify the email format for a specified domain and pull down any known emails for that domain

## Contributers

[nullg0re](https://github.com/nullg0re) - Code to gather username format and emails via Hunter.io
[nromsdahl](https://github.com/nromsdahl)

### Acknowledgements

**m8r0wn** - [CrossLinked](https://github.com/m8r0wn/CrossLinked)<br>
**initstring** - [linkedin2username](https://github.com/initstring/linkedin2username)
