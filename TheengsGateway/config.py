"""Configuration module for Theengs Gateway.

This module handles everything that has to do with configuration files and
command-line parameters for Theengs Gateway.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from importlib_metadata import version

# Each configuration option is added to:
# - the DEFAULT_CONFIG dict with its default value
# - the parse_args function for its command-line argument

DEFAULT_CONFIG = {
    "host": "",
    "port": 1883,
    "user": "",
    "pass": "",
    "ble_scan_time": 7,
    "ble_time_between_scans": 5,
    "publish_topic": "home/TheengsGateway/BTtoMQTT",
    "lwt_topic": "home/TheengsGateway/LWT",
    "subscribe_topic": "home/+/BTtoMQTT/undecoded",
    "presence_topic": "home/TheengsGateway/presence",
    "presence": 0,
    "publish_all": 1,
    "log_level": "INFO",
    "discovery": 1,
    "general_presence": 0,
    "discovery_topic": "homeassistant",
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
    "enable_tls": 0,
    "tls_insecure": 0,
    "ca_certs": None,
    "enable_websocket": 0,
    "identities": {},
    "tracker_timeout": 120,
    "ble": 1,
    "whitelist": [],
    "blacklist": [],
    "ignore_wblist": 0,
    "enable_multi_gtw_sync": 1,
    "trackersync_topic": "home/internal/trackersync",
}


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments and return them."""
    parser = argparse.ArgumentParser(
        description=f"TheengsGateway {version('TheengsGateway')}",
    )
    parser.add_argument(
        "-a",
        "--adapter",
        type=str,
        help="Bluetooth adapter (e.g. hci1 on Linux)",
    )
    parser.add_argument(
        "-b",
        "--ble",
        type=int,
        help="Enable (1) or disable (0) BLE (default: 1)",
    )
    parser.add_argument(
        "-bk",
        "--bindkeys",
        nargs="+",
        metavar=("ADDRESS", "BINDKEY"),
        help="Device addresses and their bindkeys: ADDR1 KEY1 ADDR2 KEY2",
    )
    parser.add_argument(
        "-bl",
        "--blacklist",
        nargs="+",
        help="Addresses of Bluetooth devices to ignore, all other devices are allowed",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=str(Path("~/theengsgw.conf").expanduser()),
        help="Path to the configuration file (default: ~/theengsgw.conf)",
    )
    parser.add_argument(
        "-D",
        "--discovery",
        type=int,
        help="Enable(1) or disable(0) Home Assistant MQTT discovery",
    )
    parser.add_argument(
        "-Df",
        "--discovery_filter",
        nargs="+",
        help="Device discovery filter list for Home Assistant MQTT discovery",
    )
    parser.add_argument(
        "-Dn",
        "--discovery_device_name",
        type=str,
        help="Device name for Home Assistant MQTT discovery",
    )
    parser.add_argument(
        "-Dt",
        "--discovery_topic",
        type=str,
        help="MQTT Discovery topic",
    )
    parser.add_argument(
        "-Gp",
        "--general_presence",
        type=int,
        help="Enable (1) or disable (0) general present/absent presence when --discovery: 0 (default: 0)",  # noqa: E501
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        help="MQTT host address",
    )
    parser.add_argument(
        "-id",
        "--identities",
        nargs="+",
        metavar=("ADDRESS", "IRK"),
        help="Identity addresses and their IRKs: ADDR1 IRK1 ADDR2 IRK2",
    )
    parser.add_argument(
        "-iwbl",
        "--ignore_wblist",
        type=int,
        help="Ignore a set white- or black-list (1) or not (0) (default: 0)",
    )
    parser.add_argument(
        "-Lt",
        "--lwt_topic",
        type=str,
        help="MQTT LWT topic",
    )
    parser.add_argument(
        "-ll",
        "--log_level",
        type=str,
        help="TheengsGateway log level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        help="MQTT host port",
    )
    parser.add_argument(
        "-p",
        "--pass",
        type=str,
        help="MQTT password",
    )
    parser.add_argument(
        "-pa",
        "--publish_all",
        type=int,
        help="Publish all (1) or only decoded (0) advertisements (default: 1)",
    )
    parser.add_argument(
        "-padv",
        "--publish_advdata",
        type=int,
        help="Publish advertising and advanced data (1) or not (0) (default: 0)",
    )
    parser.add_argument(
        "-pr",
        "--presence",
        type=int,
        help="Enable (1) or disable (0) presence publication (default: 1)",
    )
    parser.add_argument(
        "-prt",
        "--presence_topic",
        type=str,
        help="MQTT presence topic",
    )
    parser.add_argument(
        "-pt",
        "--publish_topic",
        type=str,
        help="MQTT publish topic",
    )
    parser.add_argument(
        "-s",
        "--scanning_mode",
        type=str,
        choices=("active", "passive"),
        help="Scanning mode (default: active)",
    )
    parser.add_argument(
        "-sd",
        "--ble_scan_time",
        type=int,
        help="BLE scan duration (seconds)",
    )
    parser.add_argument(
        "-st",
        "--subscribe_topic",
        type=str,
        help="MQTT subscribe topic",
    )
    parser.add_argument(
        "-tb",
        "--ble_time_between_scans",
        type=float,
        help="Seconds to wait between scans",
    )
    parser.add_argument(
        "-tf",
        "--time_format",
        type=int,
        help="Use 12-hour (1) or 24-hour (0) time format for clocks (default: 0)",
    )
    parser.add_argument(
        "-ca",
        "--ca_certs",
        type=str,
        help="Path to file containing local Certificate Authorities for TLS validation",
    )
    parser.add_argument(
        "-ti",
        "--tls_insecure",
        type=int,
        help="Allow (1) or disallow (0: default) insecure TLS (no hostname check)",
    )
    parser.add_argument(
        "-tls",
        "--enable_tls",
        type=int,
        help="Enable (1) or disable (0) TLS (default: 0)",
    )
    parser.add_argument(
        "-to",
        "--tracker_timeout",
        type=int,
        help="Tracker timeout duration (seconds)",
    )
    parser.add_argument(
        "-ts",
        "--time_sync",
        nargs="+",
        help="Addresses of Bluetooth devices to synchronize the time",
    )
    parser.add_argument(
        "-u",
        "--user",
        type=str,
        help="MQTT username",
    )
    parser.add_argument(
        "-wl",
        "--whitelist",
        nargs="+",
        help="Addresses of Bluetooth devices to allow, all other devices are ignored",
    )
    parser.add_argument(
        "-ws",
        "--enable_websocket",
        type=int,
        help="Enable (1) or disable (0) WebSocket (default: 0)",
    )
    parser.add_argument(
        "-gs",
        "--enable_multi_gtw_sync",
        type=int,
        help="Disable (0) or enable (1) to use tracker and closest control devices sync across Theengs Gateway gateways and OpenMQTTGateway (default: 1)",  # noqa: E501
    )
    parser.add_argument(
        "-tt",
        "--trackersync_topic",
        type=str,
        help="Internal trackersync publish topic",
    )
    return parser.parse_args()


def read_configuration(config_path: Path) -> dict:
    """Read a Theengs Gateway configuration from a file.

    If the path doesn't exist, the function returns the default configuration.
    """
    try:
        with config_path.open(encoding="utf-8") as config_file:
            configuration = json.load(config_file)
    except OSError:
        configuration = DEFAULT_CONFIG
    except json.JSONDecodeError as exception:
        msg = f"Malformed configuration file {config_path.resolve()}: {exception}"
        raise SystemExit(msg) from exception

    return configuration


def write_configuration(configuration: dict, config_path: Path) -> None:
    """Write a Theengs Gateway configuration to a file."""
    try:
        with config_path.open(encoding="utf-8", mode="w") as config_file:
            config_file.write(
                json.dumps(configuration, sort_keys=True, indent=4),
            )
    except OSError as exception:
        msg = f"Unable to write configuration file {config_path.resolve()}"
        raise SystemExit(msg) from exception


def merge_args_with_config(config: dict, args: argparse.Namespace) -> None:
    """Merge command-line arguments into configuration.

    Command-line arguments override the corresponding configuration if they are set.
    Lists and dicts are merged.
    """
    for key, value in args.__dict__.items():
        if value is not None:
            if isinstance(value, list):
                if key in {"bindkeys", "identities"}:
                    config[key].update(
                        dict(zip(value[::2], value[1::2])),
                    )
                else:
                    config[key].extend(
                        element for element in value if element not in config[key]
                    )
            elif key != "config":
                config[key] = value
