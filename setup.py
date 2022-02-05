from skbuild import setup
from packaging.version import LegacyVersion
from skbuild.exceptions import SKBuildError
from skbuild.cmaker import get_cmake_version

# Add CMake as a build requirement if cmake is not installed or is too low a version
setup_requires = []
try:
    if LegacyVersion(get_cmake_version()) < LegacyVersion("3.4"):
        setup_requires.append('cmake')
except SKBuildError:
    setup_requires.append('cmake')

setup(
    name="TheengsGateway",
    version="0.1.0",
    description="A message decoder for the Internet of Things",
    author="Theengs",
    url="https://github.com/theengs/gateway",
    license=" GPL-3.0 License",
    package_dir={"TheengsGateway": "TheengsGateway"},
    packages=["TheengsGateway"],
    setup_requires=setup_requires,
    include_package_data=True,
)

