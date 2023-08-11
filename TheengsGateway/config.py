"""Configuration module for Theengs Gateway.

This module handles everything that has to do with configuration files and
command-line parameters for Theengs Gateway.
"""
import argparse
import json
from pathlib import Path
from typing import Dict

# Each configuration option is added to:
# - the DEFAULT_CONFIG dict with its default value
# - the parse_args function for its command-line argument

DEFAULT_CONFIG = {
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
    "enable_tls": 0,
    "enable_websocket": 0,
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
        "-tls",
        "--enable_tls",
        type=int,
        help="Enable (1) or disable (0) TLS (default: 0)",
    )
    parser.add_argument(
        "-ws",
        "--enable_websocket",
        type=int,
        help="Enable (1) or disable (0) WebSocket (default: 0)",
    )
    return parser.parse_args()


def read_configuration(config_path: Path) -> Dict:
    """Read a Theengs Gateway configuration from a file.

    If the path doesn't exist, the function returns the default configuration.
    """
    try:
        with config_path.open(encoding="utf-8") as config_file:
            configuration = json.load(config_file)
    except OSError:
        configuration = DEFAULT_CONFIG
    except json.JSONDecodeError as exception:
        msg = f"Malformed configuration file {config_path.resolve()}: {str(exception)}"
        raise SystemExit(msg) from exception

    return configuration


def write_configuration(configuration: Dict, config_path: Path) -> None:
    """Write a Theengs Gateway configuration to a file."""
    try:
        with config_path.open(encoding="utf-8", mode="w") as config_file:
            config_file.write(
                json.dumps(configuration, sort_keys=True, indent=4),
            )
    except OSError as exception:
        msg = f"Unable to write configuration file {config_path.resolve()}"
        raise SystemExit(msg) from exception


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
            elif key != "config":
                config[key] = value
