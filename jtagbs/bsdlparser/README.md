# python-bsdl-parser

This is a [Grako][Grako]-based parser for IEEE 1149.1 Boundary-Scan Description
Language (BSDL) files.

## Requirements

* Python 3
* [Grako 3.99.9][Grako]

## Usage

First, install the Grako command from [here][Grako]. Then you can run `make` to
generate the actual parser module (`bsdl.py`).

After generating the parser module, run
`./bsdl2json.py bsdl_file.bsd > json_file.json` to convert your BSDL file to
JSON.


[Grako]: https://pypi.python.org/pypi/grako
