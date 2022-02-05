import sys

from .ble_gateway import run

try:
    arg = sys.argv[1]
except IndexError:
    raise SystemExit(f"Usage: {sys.argv[0]} /path/to/config.conf")

run(arg)