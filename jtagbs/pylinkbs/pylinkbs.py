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
from jtagbs import bsdl

class JTAGRawBS(object):
    def scan_init_chain(self):
        """Init the scan chain, checking for devices"""
        # Logic is from jtagcore_scan_and_init_chain() library
        
        self._jtag_reset()
        #Shift-IR
        self.tms_write(0b00110, 5)
        
        #Flush IR - 1024 bits ought to be enough for anyone
        self.tdo_flush(0, 1024)
        
        #Now send 1's for length measurement
        result = self.tdo_flush(1, 512)
        
        total_IR_length = 0
        
        for r in result:
            total_IR_length += bin(r).split('b')[1].count('0')
            
            if r == 0xff:
                break
        
        total_IR_length -= 1
        print("IR Length: %d"%total_IR_length)
        
        self.total_IR_length = total_IR_length
        
        #Now send 1's for BYPASS instruction to everyone
        self.tdo_flush(1, 1024)
        self.jtag_rawrw([1], [1], 1) #TMS high
        
        #Now go to Shift-DR
        self.tms_write(0b0011, 4)
        
        #Set DR to 0's
        self.tdo_flush(0, 512)
        
        #Count some 1's
        result = self.tdo_flush(1, 512)
        totaldev1 = 0
        for r in result:
            totaldev1 += bin(r).split('b')[1].count('0')
            if r == 0xff:
                break

        #Set DR to 1's
        self.tdo_flush(1, 512)
        
        #Count some 0's
        result = self.tdo_flush(0, 512)
        totaldev2 = 0
        for r in result:
            totaldev2 += bin(r).split('b')[1].count('0')
            if r == 0x00:
                break
        
        if totaldev1 != totaldev2:
            raise IOError("Chain unstable - detection failed")
            
        print("Found %d devices"%totaldev1)
        
        self.num_devices = totaldev1
        devlist = []
        
        if self.num_devices:
            
            self._jtag_reset()
            
            #Go to Shift-DR (DR loaded with device ID after reset)
            self.tms_write(0b0010, 4)
            
            #Read device ID's in sequence now
            for dev in range(0, self.num_devices):
                devid = self.tdo_flush(0, 32)
                unpackedid = struct.unpack("<I", bytes(devid))[0]
                devlist.append(unpackedid)
        
        self.device_idlist = devlist
        
        #Go to Idle
        self._jtag_reset()
        self.tdo_flush(0, 6) #clock out 6x 0's
        
        self.bsdl = [None]*self.num_devices
        
    def _jtag_reset(self):
        self.tms_write(0b11111, 5)

    def get_number_devices(self):
        """Get number of devices detected in the chain"""
        
        return self.num_devices

    def get_devid(self, device_number):
        """Get a given device IDCODE from the chain"""

        return self.device_idlist[device_number]


    def bsdl_attach(self, filepath, device_number, force=False):
        """Attach a BSDL file to a given device on the chain"""

        file = bsdl.BSDLFile(filepath)
        
        idmask, fileidcode = file.get_idcode()
        scanchainidcode = self.get_devid(device_number)
        
        if (fileidcode & idmask) != (scanchainidcode & idmask):
            if force == False:
                raise IOError("BSDL file idcode: %s, detected idcode %s"%(fileidcode, scanchainidcode))
        
        self.bsdl[device_number] = file


    def get_bsdl_id(self, filepath):
        """Find the device id in a BSDL file (useful to match files)"""

        raise NotImplementedError("oops")

    def get_number_of_pins(self, device_number):
        """Get total number of pins in device"""

        return len(self.bsdl[device_number].io_regs)

    def get_pin_id(self, device_number, pinname):
        """Convert a pin name to a pin number/id"""
        return

    def get_pin_state(self, device_number, pinid, pintype="input"):
        """Get state of a pin register (normally input)"""

        if isinstance(pinid, str):
            pinid = self.pin_get_id(device_number, pinid)
        
        raise NotImplementedError("oops")

    def get_pin_properties(self, device_number, pinid):
        """Get pin name & type from numeric pin id"""

        pin = self.bsdl[device_number].io_regs[pinid]
        
        #return {"name":pin[, "location":"", "type":pintype}

    def set_pin_state(self, device, pinid, state, pintype):
        """Set or clear a bit in a given output register (output or oe)"""

        raise NotImplementedError("oops")
        
    def set_scan_mode(self, device_number, mode):
        """Set scan mode to passive (sample), active (extest), or bypass"""
        raise NotImplementedError("oops")

    def scan(self, write_only=False):
        """Perform an update of the JTAG chain status, can do writeonly to ignore inputs"""
        
        if self.num_devices:
            #Go to shift-DR state
            self.tms_write(0b0010, 4)
            
            for d in range(0, self.num_devices):
                pass
                
    def tms_write(self, value, bits):
        """Write a sequence out TMS, keeping TDO low, and return result"""
        if bits > 8:
            raise AttributeError("oops my bad")
        
        return self.jtag_rawrw([0], [value], bits)
    
    def tdo_flush(self, flushval, bits):
        """Write a constant 1 or 0 out TDO, keeping TMS low, and return result"""
        bytes = int(((bits%8)+bits) / 8)
        if flushval:
            return self.jtag_rawrw([0xff]*bytes, [0]*bytes, bits)
        else:
            return self.jtag_rawrw([0]*bytes, [0]*bytes, bits)
            
    def jtag_rawrw(self, tdo, tms, num_bits=None):
        raise NotImplementedError("you need this function!!!!!")

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

    def jtag_rawrw(self, tdo, tms, num_bits=None):
        return self.jlink.jtag_rawrw(tdo, tms, num_bits)