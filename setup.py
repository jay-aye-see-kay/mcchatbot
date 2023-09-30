#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="mcchatbot",
    version="0.2",
    # Modules to import from other scripts:
    packages=find_packages(),
    # Executables
    scripts=["mcchatbot.py"],
)
