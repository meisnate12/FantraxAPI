import os, tmdbapis

from setuptools import setup, find_packages

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
    name=tmdbapis.__package_name__,
    version=__version__,
    description=tmdbapis.__description__,
    long_description=long_descr,
    url=tmdbapis.__url__,
    author=tmdbapis.__author__,
    author_email=tmdbapis.__email__,
    license=tmdbapis.__license__,
    packages=find_packages(),
    python_requires=">=3.8",
    keywords=["tmdbapis", "tmdbapi", "tmdb", "wrapper", "api"],
    install_requires=[
      "requests"
    ],
    project_urls={
      "Documentation": "https://tmdbapis.metamanager.wiki",
      "Funding": "https://github.com/sponsors/meisnate12",
      "Source": "https://github.com/meisnate12/TMDbAPIs",
      "Issues": "https://github.com/meisnate12/TMDbAPIs/issues",
    },
    classifiers=[
      "Development Status :: 5 - Production/Stable",
      "Intended Audience :: Developers",
      "Topic :: Software Development :: Libraries",
      "Programming Language :: Python",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: 3.9",
      "Programming Language :: Python :: 3.10",
      "Programming Language :: Python :: 3.11",
      "Programming Language :: Python :: 3.12",
    ]
)

