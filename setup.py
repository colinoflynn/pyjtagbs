#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'pyjtagbs',
    version = '1.0.0',
    description = "JTAG with the BS (Boundary Scan)",
    author = "Colin O'Flynn",
    author_email = 'coflynn@newae.com',
    license = 'LGPLv2.1',
    url = 'http://www.newae.com',
    download_url='https://github.com/colinoflynn/pyjtagbs',
    packages = ['jtagbs',
                ],
    install_requires = [
    ],
)
