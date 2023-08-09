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

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from .ble_gateway import run

default_config = {
    "host": "",
    "port": 1883,
    "user": "",
    "pass": "",
    "ble_scan_time": 5,
    "ble_time_between_scans": 5,
    "publish_topic": "home/TheengsGateway/BTtoMQTT",
    "lwt_topic": "home/TheengsGateway/LWT",
    "subscribe_topic": "home/+/BTtoMQTT/undecoded",
    "presence_topic": "home/TheengsGateway/presence",
    "presence": 0,
    "publish_all": 1,
    "log_level": "INFO",
    "discovery": 1,
    "hass_discovery": 1,
    "discovery_topic": "homeassistant/sensor",
    "discovery_device_name": "TheengsGateway",
    "discovery_filter": [
        "IBEACON",
    ],
    "adapter": "",
    "scanning_mode": "active",
    "time_sync": [],
    "time_format": 0,
    "publish_advdata": 0,
    "bindkeys": {},
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments and return them."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        help="MQTT host address",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        help="MQTT host port",
    )
    parser.add_argument(
        "-u",
        "--user",
        type=str,
        help="MQTT username",
    )
    parser.add_argument(
        "-p",
        "--pass",
        type=str,
        help="MQTT password",
    )
    parser.add_argument(
        "-pt",
        "--pub_topic",
        type=str,
        help="MQTT publish topic",
    )
    parser.add_argument(
        "-st",
        "--sub_topic",
        type=str,
        help="MQTT subscribe topic",
    )
    parser.add_argument(
        "-Lt",
        "--lwt_topic",
        type=str,
        help="MQTT LWT topic",
    )
    parser.add_argument(
        "-prt",
        "--presence_topic",
        type=str,
        help="MQTT presence topic",
    )
    parser.add_argument(
        "-pr",
        "--presence",
        type=int,
        help="Enable (1) or disable (0) presence publication (default: 1)",
    )
    parser.add_argument(
        "-pa",
        "--publish_all",
        type=int,
        help="Publish all (1) or only decoded (0) advertisements (default: 1)",
    )
    parser.add_argument(
        "-sd",
        "--scan_duration",
        type=int,
        help="BLE scan duration (seconds)",
    )
    parser.add_argument(
        "-tb",
        "--time_between",
        type=int,
        help="Seconds to wait between scans",
    )
    parser.add_argument(
        "-ll",
        "--log_level",
        type=str,
        help="TheengsGateway log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "-Dt",
        "--discovery-topic",
        type=str,
        help="MQTT Discovery topic",
    )
    parser.add_argument(
        "-D",
        "--discovery",
        type=int,
        help="Enable(1) or disable(0) MQTT discovery",
    )
    parser.add_argument(
        "-Dh",
        "--hass_discovery",
        type=int,
        help="Enable(1) or disable(0) Home Assistant MQTT discovery "
        "(default: 1)",
    )
    parser.add_argument(
        "-Dn",
        "--discovery_name",
        type=str,
        help="Device name for Home Assistant",
    )
    parser.add_argument(
        "-Df",
        "--discovery_filter",
        nargs="+",
        help="Device discovery filter list for Home Assistant",
    )
    parser.add_argument(
        "-a",
        "--adapter",
        type=str,
        help="Bluetooth adapter (e.g. hci1 on Linux)",
    )
    parser.add_argument(
        "-s",
        "--scanning_mode",
        type=str,
        choices=("active", "passive"),
        help="Scanning mode (default: active)",
    )
    parser.add_argument(
        "-ts",
        "--time_sync",
        nargs="+",
        help="Addresses of Bluetooth devices to synchronize the time",
    )
    parser.add_argument(
        "-tf",
        "--time_format",
        type=int,
        help="Use 12-hour (1) or 24-hour (0) time format for clocks "
        "(default: 0)",
    )
    parser.add_argument(
        "-padv",
        "--publish_advdata",
        type=int,
        help="Publish advertising and advanced data (1) or not (0) (default: 0)",
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="conf_path",
        type=str,
        default=str(Path("~/theengsgw.conf").expanduser()),
        help="Path to the configuration file (default: ~/theengsgw.conf)",
    )
    parser.add_argument(
        "-bk",
        "--bindkeys",
        nargs="+",
        metavar=("ADDRESS", "BINDKEY"),
        help="Device addresses and their bindkeys: ADDR1 KEY1 ADDR2 KEY2",
    )
    parser.add_argument(
        "-ssl",
        "--enable_ssl",
        type=bool,
        help="Enable SSL",
    )
    parser.add_argument(
        "-ws",
        "--enable_websockets",
        type=bool,
        help="Enable websockets transport layer",
    )
    return parser.parse_args()


def merge_args_with_config(config: Dict, args: argparse.Namespace) -> None:
    """Merge command-line arguments into configuration.

    Command-line arguments override the corresponding configuration if they are set.
    Lists and dicts are merged.
    """
    for key, value in args.__dict__.items():
        if value is not None:
            if isinstance(value, list):
                if key == "bindkeys":
                    config[key].update(
                        dict(zip(value[::2], value[1::2])),
                    )
                else:
                    for element in value:
                        if element not in config[key]:
                            config[key].append(element)
            else:
                config[key] = value


def main() -> None:
    """Main entry point of the TheengsGateway program."""
    args = parse_args()
    conf_path = Path(args.conf_path)

    try:
        with conf_path.open(encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (json.JSONDecodeError, OSError):
        config = default_config

    # Merge default configuration, with data read from the configuration file
    # overriding default data.
    # This guarantees that all keys we refer to are in the dictionary.
    config = {**default_config, **config}

    merge_args_with_config(config, args)

    if not config["host"]:
        sys.exit("MQTT host is not specified")

    try:
        with conf_path.open(mode="w", encoding="utf-8") as config_file:
            config_file.write(json.dumps(config, sort_keys=True, indent=4))
    except OSError as exception:
        msg = "Unable to write config file"
        raise SystemExit(msg) from exception  # noqa: TRY003

    run(conf_path)
