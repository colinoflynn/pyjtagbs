# PyJtagBS J-Link interface via PyLink
# Copyright (c) 2021 Colin O'Flynn
#
# This file is HEAVILY based on code from "JTAG Core library", which is:
# Copyright (c) 2008 - 2021 Viveris Technologies (but also LGPGv2.1)
#
# PyJTAGBS is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# PyJTAGBS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with PyJTAGBS; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import pylink
import struct
import os
from . import bsdl
from . import JTAGRawBS

class PyLinkRawBS(JTAGRawBS):
    """Python interface for JTAG via PyLink Library (which talks to JLink)"""

    def __init__(self):
        self.jlink = pylink.JLink()

    def get_probe_names(self):
        """Get the name of returned probes"""
        probes = {}
        ems = self.jlink.connected_emulators()
        for i, em in enumerate(ems):
            em = str(em)
            probes[em] = i
        return probes

    def open_probe(self, probeid=None):
        """Try to open the given probe"""
        #TODO - ignore probeid for now
        self.jlink.open()

    def jtag_rawrw(self, tdo, tms, num_bits=None, write_only=False):
        return self.jlink.jtag_rawrw(tdo, tms, num_bits)