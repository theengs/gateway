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
import uuid
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

    # Get the MAC address of the gateway.
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]
    configuration["gateway_id"] = ":".join(
        [mac_address[i : i + 2] for i in range(0, 12, 2)]
    ).upper()

    if not configuration["host"]:
        sys.exit("MQTT host is not specified")

    # Make sure discovery_filter is a list, and convert to list 
    # if it is actually a string (Docker and HA Add-in)
    if isinstance(configuration["discovery_filter"], str):
        # Convert the string to a list by removing brackets and splitting by commas
        configuration["discovery_filter"] = configuration["discovery_filter"].strip("[]").split(",")

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
