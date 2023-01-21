# read the contents of your README file
from pathlib import Path

from packaging import version
from skbuild import setup
from skbuild.cmaker import get_cmake_version
from skbuild.exceptions import SKBuildError

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Add CMake as a build requirement if cmake is not installed
# or is too low a version
setup_requires = []
try:
    if version.parse(get_cmake_version()) < version.parse("3.4"):
        setup_requires.append("cmake")
except SKBuildError:
    setup_requires.append("cmake")

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
    setup_requires=setup_requires,
    include_package_data=True,
    install_requires=[
        "bleak>=0.15.0",
        "bluetooth-clocks<1.0",
        "paho-mqtt>=1.6.1",
    ],
)
