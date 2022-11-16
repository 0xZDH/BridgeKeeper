# BridgeKeeper

<p align="center"><img src="https://media.giphy.com/media/e9aSISpSTtU4w/giphy.gif"></p>

<p align="center">
<b>Scrape</b> employee names from search engine LinkedIn profiles<br>
<b>Hunt</b> for emails and username formats via Hunter.io<br>
<b>Transform</b> names to given username format(s)
</p>

## Usage

```
usage: bridgekeeper.py [flags]

BridgeKeeper - v1.0.0

options:
  -h, --help            show this help message and exit

Target(s):
  -c COMPANY, --company COMPANY
                        target company to search for LinkedIn profiles
                        (e.g. 'Example Ltd.')

  -n NAMES, --names NAMES
                        string (comma delimited) or file containing names
                        to be converted to usernames (format: 'First (M) Last')

Username Formatting:
  -f FORMAT, --format FORMAT
                        username format (format identifiers:
                        {first}, {middle}, {last}, {f}, {m}, {l}, [#])

  -a API, --api API     hunter.io API key for email format identification
                        and email scraping

  -d DOMAIN, --domain DOMAIN
                        domain name of target company for hunter.io email
                        format identification and email scraping

  --lower               force usernames to all lower case

  --upper               force usernames to all upper case

Search Engine Configuration:
  --depth DEPTH         number of pages deep to search each search engine
                        (Default: 5)

  --bing-cookies BING_COOKIES
                        string or cookie file for Bing search engine

  --google-cookies GOOGLE_COOKIES
                        string or cookie file for Google search engine

  --yahoo-cookies YAHOO_COOKIES
                        string or cookie file for Yahoo search engine

HTTP Configuration:
  --timeout TIMEOUT     HTTP request timeout in seconds
                        (Default: 25 seconds)

  --proxy PROXY         proxy to pass HTTP traffic through: `host:port`

Output Configuration:
  -o OUTPUT, --output OUTPUT
                        directory to write output files to
                        (Default: output)

Debug:
  --version             print the tool version and exit

  --debug               enable debug output
```

Gather employee names for a company, Example Ltd., and convert each name into an 'flast' username formatted email:<br>
`bridgekeeper.py --company "Example, Ltd." --format {f}{last}@example.com --depth 10 --output example-employees`

Gather employee names and email addresses from search engines and Hunter.io:<br>
`bridgekeeper.py --company "Example, Ltd." --domain example.com --api {API_KEY} --depth 10 --output example-employees`

Convert an already generated list of names to usernames:<br>
`bridgekeeper.py --names names.txt --format {f}{last}@example.com --output example-employees`

Username format examples (BridgeKeeper supports middle names as well as character limited usernames - e.g. only 4 characters of a last name is used):<br>
```
Name: John Adams Smith
{f}{last}                   > jsmith
{f}{m}.{last}               > ja.smith
{f}{last}[4]@example.com    > jsmit@example.com
```

## Features

* Support scraping against three major search engines: Google, Bing, and Yahoo
* Name parsing to strip LinkedIn titles, certs, prefixes, etc.
* Search engine blacklist evasion via cookie files
* Username formatting
  * Name trimming
    * e.g. If a username format has only the first 4 characters of the last name
  * Hyphenated last name handling
  * Duplicate username handling
    * Incrementing numbers appended to duplicate usernames
* Support Hunter.io scraping:
  * Identification of email format for a specified domain
  * Retrieval of known emails for a specified domain

### Acknowledgements

* **[m8r0wn](https://github.com/m8r0wn)**: [CrossLinked](https://github.com/m8r0wn/CrossLinked)
* **[initstring](https://github.com/initstring)**: [linkedin2username](https://github.com/initstring/linkedin2username)
* **[nullg0re](https://github.com/nullg0re)**: Code to gather username format and emails via Hunter.io
