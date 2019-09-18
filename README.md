# BridgeKeeper

##### Transform names into different username formats.

![Alt Text](https://media.giphy.com/media/e9aSISpSTtU4w/giphy.gif)


### Usage

```
usage: bridgekeeper.py [-h] (-l | -a | -f FORMAT | -d DESIGN) [-c COUNT]
                       [-t [{first,last}]] [-n NAMES] [-s SINGLE] [-o OUTPUT]

Name transformer.

optional arguments:
  -h, --help            show this help message and exit
  -l, --list            List all predefined username formats.
  -a, --all             Transform using all predefined username formats.
  -f FORMAT, --format FORMAT
                        Transform using a specific predefined username format.
  -d DESIGN, --design DESIGN
                        Design a custom username format to transform with.
                        Format Examples: {first}{last}, {f}{last}[4]
  -c COUNT, --count COUNT
                        How many characters to use from [First] or [Last]
                        during transform.
  -t [{first,last}], --trim [{first,last}]
                        Trim [First] or [Last] during transform.
  -n NAMES, --names NAMES
                        File containing names formatted as '[First] [Last]'.
  -s SINGLE, --single SINGLE
                        Single name formatted as '[First] [Last]'.
  -o OUTPUT, --output OUTPUT
                        Directory to write usernames to.
```

### Examples

`python bridgekeeper.py -s "John Smith" -a`

`python bridgekeeper.py -s "John Smith" -f flast`

`python bridgekeeper.py -s "John Smith" -d {f}-{last}`