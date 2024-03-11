# Copyright (c) 2024 Colin O'Flynn
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

from .jtagraw import JTAGRawBS

class JTAGCWUserIO(JTAGRawBS):
    """ ChipWhisperer JTAG access using the UserIO connector on the CW-Husky.

    ```
        from pyjtagbs.jtagbs import JTAGBS, JTAGCWUserIO

        interface = JTAGCWUserIO(scope)
        jtag = JTAGBS(interface)

        jtag.init_scanchain(verbose=True)

        print(jtag.list_devids())
        print(jtag.list_devices())

        > IR Length: 3
        > Found 1 devices
        >  [1268778103]
        >  [{'manid': '01000111011', 'pid': '1011101000000000', 'vn': '0100', 'manufacturer': 'ARM Ltd.'}]
    ```
    """
    pin_tdi = 7
    pin_tms = 6
    pin_tck = 5
    pin_tdo = 3
    
    def __init__(self, scope, enable_drive=True):
        self.scope = scope
        
        #Set this higher if detection fails
        self.flush_len = 32
        
        if enable_drive:
            self.enable()
        
    def enable(self):
        d = self.scope.userio.direction
        d |= (1<< self.pin_tdi) | (1<<self.pin_tck) | (1<<self.pin_tms)
        self.scope.userio.direction = d
        
    def tristate_tck_tdi(self):
        d = self.scope.userio.direction
        d &= ~((1<< self.pin_tdi) | (1<<self.pin_tck))
        self.scope.userio.direction = d
        
    def disable(self):
        d = self.scope.userio.direction
        d &= ~((1<< self.pin_tdi) | (1<<self.pin_tck) | (1<<self.pin_tms))
        self.scope.userio.direction = d
        
    def jtag_rawrw(self, tdo, tms, num_bits=None, write_only=False):
        
        byte = 0
        bit = 0
        read = []
        read_temp = 0
        for _ in range(0, num_bits):
            d = self.scope.userio.drive_data
            d &= ~((1<< self.pin_tdi) | (1<<self.pin_tms))
            
            if not write_only:
                tdostatus = self.scope.userio.status
                tdostatus = (tdostatus >> self.pin_tdo) & 1
            
            if bit == 8:
                byte += 1
                bit = 0                
                read.append(read_temp)
                read_temp = 0
            
            tdobit = (tdo[byte] >> bit) & 1
            tmsbit = (tms[byte] >> bit) & 1           
            
            if tdobit:
                d |= (1<<self.pin_tdi)
            
            if tmsbit:
                d |= (1<<self.pin_tms)
            
            self.scope.userio.drive_data = d
            self.scope.userio.drive_data = d | (1<<self.pin_tck)
            self.scope.userio.drive_data = d & ~(1<<self.pin_tck)
            
            if not write_only:
                read_temp |= (tdostatus << bit)
            
            bit += 1
            
        read.append(read_temp)
        if write_only:
            return None
        else:
            return read