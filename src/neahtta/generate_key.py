#!/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import binascii
import os

print(binascii.hexlify(os.urandom(24)))
