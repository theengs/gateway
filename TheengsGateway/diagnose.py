"""Diagnose module for Theengs Gateway.

This module can be run on the command line with python -m TheengsGateway.diagnose
to show diagnostic information for debugging purposes.
"""
import asyncio
import json
import os
import platform
import re
import sys

from importlib_metadata import PackageNotFoundError, version

_conf_path = os.path.expanduser("~") + "/theengsgw.conf"
_ADDR_RE = re.compile(r"^(([0-9A-F]{2}:){3})([0-9A-F]{2}:){2}[0-9A-F]{2}$")


def _anonymize_strings(fields, config) -> None:
    for field in fields:
        if field in config:
            config[field] = "***"


def _anonymize_address(address) -> str:
    addr_parts = _ADDR_RE.match(address)
    if addr_parts:
        return f"{addr_parts.group(1)}XX:XX:XX"
    else:
        return "INVALID ADDRESS"


def _anonymize_addresses(field, config) -> None:
    try:
        config[field] = [
            _anonymize_address(address) for address in config[field]
        ]
    except KeyError:
        pass


# This function is taken from Textual
def _section(title, values) -> None:
    """Print a collection of named values within a titled section."""
    max_name = max(map(len, values.keys()))
    max_value = max(map(len, [str(value) for value in values.values()]))
    print(f"## {title}")
    print()
    print(f"| {'Name':{max_name}} | {'Value':{max_value}} |")
    print(f"|-{'-' * max_name}-|-{'-'*max_value}-|")
    for name, value in values.items():
        print(f"| {name:{max_name}} | {str(value):{max_value}} |")
    print()


def _versions() -> None:
    """Print useful version numbers."""
    try:
        packages = {
            "Theengs Gateway": version("TheengsGateway"),
            "Theengs Decoder": version("TheengsDecoder"),
            "Bleak": version("bleak"),
            "Bluetooth Clocks": version("bluetooth-clocks"),
            "Bluetooth Numbers": version("bluetooth-numbers"),
            "Paho MQTT": version("paho-mqtt"),
        }
    except PackageNotFoundError as e:
        print(f"Package {e.name} not found. Please install it with:")
        print()
        print(f"    pip install {e.name}")
        print()

    if sys.version_info[:2] >= (3, 9):
        try:
            packages["Bluetooth Adapters"] = version("bluetooth-adapters")
        except PackageNotFoundError as e:
            print(f"Package {e.name} not found. Please install it with:")
            print()
            print(f"    pip install {e.name}")
            print()

    _section("Package Versions", packages)


def _python() -> None:
    """Print information about Python."""
    _section(
        "Python",
        {
            "Version": platform.python_version(),
            "Implementation": platform.python_implementation(),
            "Compiler": platform.python_compiler(),
            "Executable": sys.executable,
        },
    )


def _os() -> None:
    """Print operating system information."""
    os_parameters = {
        "System": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine type": platform.machine(),
    }
    if platform.system() == "Linux" and sys.version_info[:2] >= (3, 10):
        os_parameters["Distribution"] = platform.freedesktop_os_release()[
            "PRETTY_NAME"
        ]

    _section("Operating System", os_parameters)


def _config() -> None:
    """Print the anonymized Theengs Gateway configuration."""
    print("## Configuration")
    print()
    try:
        with open(_conf_path, encoding="utf-8") as config_file:
            config = json.load(config_file)
            _anonymize_strings(["user", "pass"], config)
            _anonymize_addresses("time_sync", config)
        print("```")
        print(json.dumps(config, sort_keys=True, indent=4))
        print("```")
        print()
    except FileNotFoundError:
        print(f"Configuration file not found: {_conf_path}")
        print()


async def _adapters() -> None:
    """Print information about the system's Bluetooth adapters."""
    if sys.version_info[:2] >= (3, 9):
        from bluetooth_adapters import get_adapters

        print("## Bluetooth adapters")
        print()
        bluetooth_adapters = get_adapters()
        await bluetooth_adapters.refresh()
        print(f"Default adapter: {bluetooth_adapters.default_adapter}")
        print()

        for adapter, properties in sorted(bluetooth_adapters.adapters.items()):
            properties["address"] = _anonymize_address(properties["address"])
            print("#", end="")
            _section(adapter, properties)


async def diagnostics():
    """Main function of the diagnose module.

    This function prints a header and various sections with diagnostic information
    about package versions, Python and operating system information, the
    anonymized configuration file and Bluetooth adapter information in Markdown
    format.
    """
    print("# Theengs Gateway Diagnostics")
    print()
    _versions()
    _python()
    _os()
    _config()
    await _adapters()


if __name__ == "__main__":
    asyncio.run(diagnostics())
