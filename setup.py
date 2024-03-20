#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'pyjtagbs',
    version = '1.0.1',
    description = "JTAG with the BS (Boundary Scan)",
    author = "Colin O'Flynn",
    author_email = 'colin@oflynn.com',
    license = 'LGPLv2.1',
    url = 'http://www.colinoflynn.com',
    download_url='https://github.com/colinoflynn/pyjtagbs',
    packages = [find_packages()],
    install_requires = [
    ],
)
