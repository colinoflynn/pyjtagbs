#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'pyjtagbs',
    version = '1.0.0',
    description = "JTAG without the BS",
    author = "Colin O'Flynn",
    author_email = 'coflynn@newae.com',
    license = 'GPLv3',
    url = 'http://www.newae.com',
    download_url='https://github.com/colinoflynn/pyjtagbs',
    packages = ['jtagbs',
                ],
    install_requires = [
    ],
)
