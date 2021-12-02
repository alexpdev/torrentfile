#! /usr/bin/python3
# -*- coding: utf-8 -*-

#############################################################################
# Copyright (C) 2021 alexpdev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
############################################################################
"""Setup for Torrentfile package."""

import json
from setuptools import find_packages, setup


def load_info():
    """Extract information from package.json."""
    return json.load(open("package.json"))


def load_description():
    """Load readme into long description parameter."""
    with open("README.md", "rt", encoding="utf-8") as readme:
        long_description = readme.read()
    return long_description


INFO = load_info()

setup(
    name=INFO["name"],
    version=INFO["version"],
    description=INFO["description"],
    long_description=load_description(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU Lesser General Public License v3"
        " (LGPLv3)",
    ],
    keywords=INFO["keywords"],
    author=INFO["author"],
    author_email=INFO["email"],
    url=INFO["url"],
    project_urls={"Source Code": "https://github.com/alexpdev/torrentfile"},
    license=INFO["license"],
    packages=find_packages(exclude=["env", "tests"]),
    include_package_data=True,
    entry_points={"console_scripts": ["torrentfile = torrentfile.cli:main"]},
    tests_require=["pytest"],
    install_requires=["pyben", "tqdm"],
    setup_requires=["setuptools", "wheel"],
    zip_safe=False,
    test_suite="complete",
)
