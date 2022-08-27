from . import __version__
from .smake import Smake

import argparse
import os
import sys

parser = argparse.ArgumentParser(description="simple c/c++ build system", prog=sys.argv[0])

parser.add_argument("target", type=str, help="target to build", default="main", nargs="?")

parser.add_argument("-f", "--file", type=str, help="smake configuration file", default="smake.py", required=False)

parser.add_argument("-d", "--debug", type=bool, help="enable debug mode", required=False)
parser.add_argument("-r", "--release", type=bool, help="enable release mode", required=False)

parser.add_argument("-V", "--version", action="version", version=f"SMake {__version__}")

args = parser.parse_args()

exec(open(args.file, "r").read())

if args.release:
    Smake.DEBUG = False
if args.debug:
    Smake.DEBUG = True

Smake._build(args.target)
