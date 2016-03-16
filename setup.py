#!/usr/bin/env python

import os, sys
from setuptools import setup, find_packages

PACKAGE = 'nnnotes'

with open('README') as file:
    README = file.read()

setup(
	name = 'nnnotes',
	version = 'v0',
	packages = find_packages(),
	package_data = {PACKAGE: ['template/Makefile', 'template/*.mmd', 'template/p/*']},
	scripts = ['bin/nnnote', 'bin/iiindex', 'bin/iiinject'],
	provides=[PACKAGE],
	author = 'gauthiier',
	author_email = 'd@gauthiier.info',
	url = 'https://github.com/gauthiier/nnnotes',
	long_description=README,
	classifiers=[
        "Topic :: Utilities",
        "License :: MIT License",
    ]
)