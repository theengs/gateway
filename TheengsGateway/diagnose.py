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
    try:
        return f"{addr_parts.group(1)}XX:XX:XX"
    except AttributeError:
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
    """Print a collection of named values within a titled section.
    Args:
        title: The title for the section.
        values: The values to print out.
    """
    max_name = max(map(len, values.keys()))
    max_value = max(map(len, values.values()))
    print(f"## {title}")
    print()
    print(f"| {'Name':{max_name}} | {'Value':{max_value}} |")
    print(f"|-{'-' * max_name}-|-{'-'*max_value}-|")
    for name, value in values.items():
        print(f"| {name:{max_name}} | {value:{max_value}} |")
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
    os_parameters = {
        "System": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Machine type": platform.machine(),
    }
    if platform.system() == "Linux":
        os_parameters["Distribution"] = platform.freedesktop_os_release()[
            "PRETTY_NAME"
        ]

    _section("Operating System", os_parameters)


def _config() -> None:
    print("## Configuration")
    print()
    try:
        with open(_conf_path, encoding="utf-8") as config_file:
            config = json.load(config_file)
            _anonymize_strings(["user", "pass"], config)
            _anonymize_addresses("time_sync", config)
        print(json.dumps(config, sort_keys=True, indent=4))
        print()
    except FileNotFoundError:
        print(f"Configuration file not found: {_conf_path}")
        print()


async def _adapters() -> None:
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
            for prop in properties:
                properties[prop] = str(properties[prop])
            print("#", end="")
            _section(adapter, properties)


async def diagnostics():
    print("# Theengs Gateway Diagnostics")
    print()
    _versions()
    _python()
    _os()
    _config()
    await _adapters()


if __name__ == "__main__":
    asyncio.run(diagnostics())
