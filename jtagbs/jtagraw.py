# Copyright (c) 2021 - 2024 Colin O'Flynn
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

import struct
import math

from enum import Enum

class Jtagstate(Enum):
    TEST_LOGIC_RESET = 0
    RUN_TEST_IDLE = 1
    SELECT_DRSCAN = 2
    CAPTURE = 3
    SHIFT = 4
    EXIT1 = 5
    PAUSE = 6
    EXIT2 = 7
    UPDATE = 8

def split_input_to_bytes(value, bit_length=None):
    """
    Splits an integer into a sequence of 8-bit bytes or returns the list if the input is already a list.

    Args:
    - value (int or List[int]): The integer to split or a list of integers.
    - bit_length (int, optional): The total length in bits of the integer. Not used if value is a list.

    Returns:
    - List[int]: A list of integers, where each integer is an 8-bit byte, or the original list.
    """
    # Check if the input is already a list
    if isinstance(value, list):
        return value
    
    bytes_list = []
    # Ensure we process the correct number of bits by zero-filling on the right if necessary
    value = value & ((1 << bit_length) - 1)
    
    while bit_length > 0:
        # Extract 8 bits at a time
        byte = value & 0xFF
        bytes_list.append(byte)
        # Shift right by 8 bits
        value >>= 8
        bit_length -= 8
    
    # Reverse the list to have bytes in order from most significant to least significant
    return bytes_list

class JTAGRawBS(object):
    """Raw JTAG access object using only Python, no external DLL needed!
    
    Reimplement this class with the `jtag_rawrw()` implemented.
    """

    flush_len = 512
    state = Jtagstate.TEST_LOGIC_RESET

    def scan_init_chain(self, verbose=False):
        """Init the scan chain, checking for devices"""
        # Logic is from jtagcore_scan_and_init_chain() library
        
        self._jtag_reset()
        #Shift-IR
        self.tms_write(0b00110, 5)
        
        #Flush IR - 1024 bits ought to be enough for anyone
        self.tdo_flush(0, self.flush_len*2, write_only=True)
        
        #Now send 1's for length measurement
        result = self.tdo_flush(1, self.flush_len)
        
        total_IR_length = 0
        
        for r in result:
            total_IR_length += bin(r).split('b')[1].count('0')
            
            if r == 0xff:
                break
        
        total_IR_length -= 1
        
        if verbose:
            print("IR Length: %d"%total_IR_length)
        
        self.total_IR_length = total_IR_length
        
        #Now send 1's for BYPASS instruction to everyone
        self.tdo_flush(1, self.flush_len*2, write_only=True)
        self.jtag_rawrw([1], [1], 1) #TMS high
        
        #Now go to Shift-DR
        self.tms_write(0b0011, 4)
        
        #Set DR to 0's
        self.tdo_flush(0, self.flush_len, write_only=True)
        
        #Count some 1's
        result = self.tdo_flush(1, self.flush_len)
        totaldev1 = 0
        for r in result:
            totaldev1 += bin(r).split('b')[1].count('0')
            if r == 0xff:
                break

        #Set DR to 1's
        self.tdo_flush(1, self.flush_len, write_only=True)
        
        #Count some 0's
        result = self.tdo_flush(0, self.flush_len)
        totaldev2 = 0
        for r in result:
            totaldev2 += bin(r).split('b')[1].count('1')
            if r == 0x00:
                break
        
        if totaldev1 != totaldev2:
            raise IOError("Chain unstable - detection failed\n  Scan1:%s\n  Scan2:%s"%(totaldev1, totaldev2))
        
        if verbose:
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
        self.state = Jtagstate.RUN_TEST_IDLE
        
        self.bsdl = [None]*self.num_devices

        
    def _jtag_reset(self):
        self.tms_write(0b11111, 5)
        self.state = Jtagstate.TEST_LOGIC_RESET

    def measure_DR_length(self, max=100):
        if self.state == Jtagstate.TEST_LOGIC_RESET:
            # Capture DR state then shiftDR state
            self.tms_write(0b0010, 4)
        elif self.state == Jtagstate.RUN_TEST_IDLE:
            self.tms_write(0b001, 3)
        elif self.state == Jtagstate.SELECT_DRSCAN:
            self.tms_write(0b00, 2)
        else:
            raise IOError("Unhandled JTAG State: " + str(self.state))
        
        #Clear register to 0
        bcount = math.ceil(max / 8.0)
        default_value = self.jtag_rawrw([0]*bcount, [0]*bcount, max)

        #Send a single 1 to start
        self.jtag_rawrw([1], [0], 1)

        length = -1
        for i in range(1, max):
            resp = self.jtag_rawrw([0], [0], 1)
            if resp[0] == 1:
                length = i
                break
        
        self.tms_write(0b011, 3)
        self.state = Jtagstate.RUN_TEST_IDLE
        
        return length, default_value


    def read_DR(self, bits, return_to_idle=True, pause_dr=False):
        """
        Reads from the data register. If `return_to_idle` is false goes back to SCAN-DR state.

        `pause_dr` goes through the PAUSE-DR state BEFORE shifting, which is used to exit TAP modes
         on certain MCUs (SPC etc) and return to normal operation.
        """
        bcount = math.ceil(bits / 8.0)        

        if pause_dr:
            #Go to pause DR first, then shift-DR
            if self.state == Jtagstate.TEST_LOGIC_RESET:
                # Capture DR state then shiftDR state
                self.tms_write(0b0101010, 7)
            elif self.state == Jtagstate.RUN_TEST_IDLE:
                self.tms_write(0b010101, 6)
            elif self.state == Jtagstate.SELECT_DRSCAN:
                self.tms_write(0b01010, 5)
            else:
                raise IOError("Unhandled JTAG State: " + str(self.state))
        else:
            if self.state == Jtagstate.TEST_LOGIC_RESET:
                # Capture DR state then shiftDR state
                self.tms_write(0b0010, 4)
            elif self.state == Jtagstate.RUN_TEST_IDLE:
                self.tms_write(0b001, 3)
            elif self.state == Jtagstate.SELECT_DRSCAN:
                self.tms_write(0b00, 2)
            else:
                raise IOError("Unhandled JTAG State: " + str(self.state))

        # Read output
        if bits > 0:
            tms = split_input_to_bytes((1<<(bits-1)), bits)
            output = self.jtag_rawrw([0]*bcount, tms, bits)
        else:
            self.tms_write(0b1, 1)
            output = None

        #Back to idle
        if return_to_idle:
            self.tms_write(0b01, 2)
            self.state = Jtagstate.RUN_TEST_IDLE
        else:
            self.tms_write(0b11, 2)
            self.state = Jtagstate.SELECT_DRSCAN
        
        return output
    
    def write_DR(self, data, bits, return_to_idle=True, callback_before_updatedr=None):
        """Write to DR and return to idle, must be in idle state to start"""
        data = split_input_to_bytes(data, bits)
        tms = split_input_to_bytes((1<<(bits-1)), bits)
        
        if self.state == Jtagstate.TEST_LOGIC_RESET:
            # Capture DR state then shiftDR state
            self.tms_write(0b0010, 4)
        elif self.state == Jtagstate.RUN_TEST_IDLE:
            self.tms_write(0b001, 3)
        elif self.state == Jtagstate.SELECT_DRSCAN:
            self.tms_write(0b00, 2)
        else:
            raise IOError("Unhandled JTAG State: " + str(self.state))
        
        #Send the data
        self.jtag_rawrw(data, tms, bits, write_only=True)

        if callback_before_updatedr:
            callback_before_updatedr()

        #Back to idle
        if return_to_idle:
            self.tms_write(0b01, 2)
            self.state = Jtagstate.RUN_TEST_IDLE
        else:
            self.tms_write(0b11, 2)
            self.state = Jtagstate.SELECT_DRSCAN
    
    def write_IR(self, data, bits, return_to_idle=True, callback_before_updateir=None):
        """Write to IR and return to idle, must be in idle state to start"""
        data = split_input_to_bytes(data, bits)
        tms = split_input_to_bytes((1<<(bits-1)), bits)

        #Go to shift-IR state
        self.tms_write(0b00110, 5)
        
        #Send the data, with TMS set to '1' on last bit
        self.jtag_rawrw(data, tms, bits, write_only=True)

        if callback_before_updateir:
            callback_before_updateir()

        #Back to idle
        if return_to_idle:
            self.tms_write(0b01, 2)
            self.state = Jtagstate.RUN_TEST_IDLE
        else:
            self.tms_write(0b11, 2)
            self.state = Jtagstate.SELECT_DRSCAN

    def nexus_32bit_read_write_CR(self, register_index_wr, register_data):
        """Write to CR and return to SELECT-DR, must start in SELECT-DR"""

        if self.state == Jtagstate.RUN_TEST_IDLE:
            self.tms_write(0b0010, 4)
        elif self.state == Jtagstate.SELECT_DRSCAN:
            #Go to shift-DR state
            self.tms_write(0b00, 2)
        else:
            raise IOError("Must be in SELECT-DR state, not "+str(self.state))

        #Send the register index
        self.jtag_rawrw([register_index_wr], [1<<7], 8)#, write_only=True)
        
        #Go Update-DR->Shift DR
        self.tms_write(0b0011, 4)
        
        # Data should be 32 bits
        bits = 32
        tms = split_input_to_bytes((1<<(bits-1)), bits)
        data = split_input_to_bytes(register_data, bits)
        old_value = self.jtag_rawrw(data, tms, bits)

        #Back to IDLE
        self.tms_write(0b01, 2)
        self.state = Jtagstate.RUN_TEST_IDLE
        
        return old_value

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
    
    def tdo_flush(self, flushval, bits, write_only=False):
        """Write a constant 1 or 0 out TDO, keeping TMS low, and return result"""
        bytes = int(((bits%8)+bits) / 8)
        if flushval:
            return self.jtag_rawrw([0xff]*bytes, [0]*bytes, bits, write_only)
        else:
            return self.jtag_rawrw([0]*bytes, [0]*bytes, bits, write_only)
            
    def jtag_rawrw(self, tdo, tms, num_bits=None, write_only=False):
        raise NotImplementedError("you need this function!!!!!")