#!/bin/env python
from secrets import token_hex
from sys import exit, argv

filename = "secret_key.do.not.check.in"

quiet = "-q" in argv

try:
    with open(filename, "x") as f:
        f.write(token_hex(24))
except FileExistsError:
    if not quiet:
        print(f"file {filename} already exists")
    exit(1)
else:
    exit(0)
