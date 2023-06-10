"""Setup script for TheengsGateway package."""
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="TheengsGateway",
    version="version_tag",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Theengs",
    url="https://github.com/theengs/gateway",
    license="GPL-3.0 License",
    package_dir={"TheengsGateway": "TheengsGateway"},
    packages=["TheengsGateway"],
    scripts=["bin/TheengsGateway"],
    include_package_data=True,
    install_requires=[
        "bleak>=0.19.0",
        'bluetooth-adapters>=0.15.3; python_version>="3.9"',
        "bluetooth-clocks<1.0",
        "bluetooth-numbers>=1.0,<2.0",
        "importlib-metadata",
        "paho-mqtt>=1.6.1",
        "TheengsDecoder>=1.5.0",
    ],
)
