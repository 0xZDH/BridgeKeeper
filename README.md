# BridgeKeeper

##### Transform names into different username formats.

<p align="center"><img src="https://media.giphy.com/media/e9aSISpSTtU4w/giphy.gif"></p>


### Usage

```
usage: bridgekeeper.py [-h] (-l | -a | -f FORMAT | -d DESIGN) [-c COUNT]
                       [-t TRIM] [-n NAMES] [-s SINGLE] [-o OUTPUT]

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
  -c COUNT, --count COUNT
                        Number of characters to keep when trimming during
                        transform. Must be used with -t/--trim
  -t TRIM, --trim TRIM  Trim one of the following during transform: 'first',
                        'last', 'f', 'l'. Must be used with -c/--count
  -n NAMES, --names NAMES
                        File containing names formatted as 'First Last'.
  -s SINGLE, --single SINGLE
                        Single name formatted as 'First Last'.
  -o OUTPUT, --output OUTPUT
                        Directory to write username files to.
```

### Examples

`python bridgekeeper.py -s "John Smith" -a`

`python bridgekeeper.py -s "John Smith" -f flast`

`python bridgekeeper.py -s "John Smith" -d {f}-{last}`