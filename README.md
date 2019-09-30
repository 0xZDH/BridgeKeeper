# BridgeKeeper

<p align="center"><img src="https://media.giphy.com/media/e9aSISpSTtU4w/giphy.gif"></p>

Transform names into various username formats.

### Usage

```
usage: bridgekeeper.py [-h] (-l | -a | -f FORMAT | -d DESIGN) [-F FILE]
                       [-s SINGLE] [-o OUTPUT]

Name transformer.

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List all predefined username formats.
  -a, --all             Transform using all predefined username formats.
  -f FORMAT, --format FORMAT
                        Transform using a specific predefined username format.
  -d DESIGN, --design DESIGN
                        Design a custom username format to transform with.
                        Format Examples: {first}x{last}, {f}-{last}
  -F FILE, --file FILE  File containing names formatted as 'First Last'.
  -s SINGLE, --single SINGLE
                        Single name formatted as 'First Last'.
  -o OUTPUT, --output OUTPUT
                        Directory to write username files to.
```

### Examples

Transform a name to all predefined username formats:<br>
`python bridgekeeper.py -s "John Adams Smith" -a`

Transform a name to a specified predefined username format:<br>
`python bridgekeeper.py -s "John Adams Smith" -f flast`

Transform a name to a user designed username format:<br>
`python bridgekeeper.py -s "John Adams Smith" -d {f}{m}-{last}`

Trim usernames ([#] indicates the number of characters to use: Smith[4] -> Smit):<br>
`python bridgekeeper.py -s "John Adams Smith" -d {first}[2]-{last}[4]`
