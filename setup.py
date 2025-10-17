import os

from setuptools import find_packages, setup

import fantraxapi

with open("README.rst", "r") as f:
    long_descr = f.read()

__version__ = None
if os.path.exists("VERSION"):
    with open("VERSION") as handle:
        for line in handle.readlines():
            line = line.strip()
            if len(line) > 0:
                __version__ = line
                break

setup(
    name=fantraxapi.__package_name__,
    version=__version__,
    description=fantraxapi.__description__,
    long_description=long_descr,
    long_description_content_type="text/x-rst",
    url=fantraxapi.__url__,
    author=fantraxapi.__author__,
    author_email=fantraxapi.__email__,
    license=fantraxapi.__license__,
    packages=find_packages(),
    python_requires=">=3.11",
    keywords=["fantraxapi", "fantrax", "fantasy", "wrapper", "api"],
    install_requires=["requests", "setuptools"],
    project_urls={
        "Documentation": "https://fantraxapi.kometa.wiki",
        "Funding": "https://github.com/sponsors/meisnate12",
        "Source": "https://github.com/meisnate12/FantraxAPI",
        "Issues": "https://github.com/meisnate12/FantraxAPI/issues",
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)
