# BridgeKeeper

<p align="center"><img src="https://media.giphy.com/media/e9aSISpSTtU4w/giphy.gif"></p>

Convert names into various username formats.

### Usage

```
usage: bridgekeeper.py [-h] [-l] [-a] [-f FORMAT] [-F FILE] [-n NAME]
                       [-o OUTPUT] [-d]

Convert name to username format.

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List all predefined username formats.
  -a, --all             Convert using all predefined username formats.
  -f FORMAT, --format FORMAT
                        Specify predefined or custom username format. Valid
                        format identifiers: {first}, {middle}, {last}, {f},
                        {m}, {l}
  -F FILE, --file FILE  File containing names formatted as 'First Last'.
  -n NAME, --name NAME  Single/List of names formatted as 'First Last'
                        delimited by a comma (,).
  -o OUTPUT, --output OUTPUT
                        Directory to write username files to.
  -d, --debug           Enable debug output.
```

### Examples

Transform a name to all predefined username formats:<br>
`$ python bridgekeeper.py -n "John Adams Smith" -a`

Transform a name to a specified predefined username format:<br>
```
$ python bridgekeeper.py -n "John Adams Smith" -f {f}{last}

{'{f}{last}': ['JSmith']}
```

Transform a name to a user designed username format:<br>
```
$ python bridgekeeper.py -n "John Adams Smith" -f {f}{m}-{last}

{'{f}{m}-{last}': ['JA-Smith']}
```

Limit characters used in a user designed username format:<br>
```
$ python bridgekeeper.py -n "John Adams Smith" -f {first}[2]-{middle}-{last}[4]

{'{first}[2]-{middle}-{last}[4]': ['Jo-Adams-Smit']}
```
