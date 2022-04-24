#! /usr/bin/python3
# -*- coding: utf-8 -*-

##############################################################################
#    Copyright (C) 2021-current alexpdev
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
##############################################################################
"""Setup for Torrentfile package."""

import json
from setuptools import find_packages, setup


def load_info():
    """Extract information from package.json and README files."""
    info = json.load(open("package.json"))
    with open("README.md", "rt", encoding="utf-8") as readme:
        info["long_description"] = readme.read()
    return info


INFO = load_info()

setup(
    name=INFO["name"],
    version=INFO["version"],
    description=INFO["description"],
    long_description=INFO["long_description"],
    long_description_content_type="text/markdown",
    classifiers=[
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License"
    ],
    keywords=INFO["keywords"],
    author=INFO["author"],
    author_email=INFO["email"],
    url=INFO["url"],
    project_urls={"Source Code": "https://github.com/alexpdev/torrentfile"},
    license=INFO["license"],
    packages=find_packages(exclude=[".env", "tests"]),
    include_package_data=True,
    entry_points={"console_scripts": ["torrentfile = torrentfile.cli:main"]},
    install_requires=["pyben>=0.3.1"],
    setup_requires=["setuptools", "wheel"],
    zip_safe=False
)
