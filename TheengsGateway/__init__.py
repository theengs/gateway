"""TheengsGateway - Decode things and devices and publish data to an MQTT broker.

Copyright: (c)Florian ROBERT

This file is part of TheengsGateway.

TheengsGateway is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

TheengsGateway is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from pathlib import Path

from .ble_gateway import run
from .config import (
    DEFAULT_CONFIG,
    merge_args_with_config,
    parse_args,
    read_configuration,
    write_configuration,
)


def main() -> None:
    """Main entry point of the TheengsGateway program."""
    args = parse_args()
    config_path = Path(args.config)

    configuration = read_configuration(config_path)
    # Merge default configuration, with data read from the configuration file
    # overriding default data.
    # This guarantees that all keys we refer to are in the dictionary.
    configuration = {**DEFAULT_CONFIG, **configuration}
    merge_args_with_config(configuration, args)

    # Remove /sensor if existing in the configuration as we now handle different types
    # of devices.
    if configuration["discovery_topic"].endswith("/sensor"):
        configuration["discovery_topic"] = configuration["discovery_topic"][:-7]

    if not configuration["host"]:
        sys.exit("MQTT host is not specified")

    # Remove possible discovery filter remnants not required after the RMAC introduction
    if "GAEN" in configuration["discovery_filter"]:
        configuration["discovery_filter"].remove("GAEN")
    if "MS-CDP" in configuration["discovery_filter"]:
        configuration["discovery_filter"].remove("MS-CDP")
    if "APPLE_CONT" in configuration["discovery_filter"]:
        configuration["discovery_filter"].remove("APPLE_CONT")
    if "APPLE_CONTAT" in configuration["discovery_filter"]:
        configuration["discovery_filter"].remove("APPLE_CONTAT")
    if "APPLEDEVICE" in configuration["discovery_filter"]:
        configuration["discovery_filter"].remove("APPLEDEVICE")
    if "APPLEWATCH" in configuration["discovery_filter"]:
        configuration["discovery_filter"].remove("APPLEWATCH")

    write_configuration(configuration, config_path)
    run(configuration, config_path)
