# PyJtagBS Python JTAG Boundary Scan
# Copyright (c) 2021 Colin O'Flynn
#
# All of the heavy lifting done by Forest Crossman's code!
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

import json
import os

from jtagbs.bsdlparser import bsdl

class BsdlSemantics:
    def map_string(self, ast):
        parser = bsdl.bsdlParser()
        ast = parser.parse(''.join(ast), "port_map")
        return ast

    def grouped_port_identification(self, ast):
        parser = bsdl.bsdlParser()
        ast = parser.parse(''.join(ast), "group_table")
        return ast
        
class BSDLFile(object):
    def __init__(self, filename):
        """Load and parse a BSDL file."""

        if not os.path.exists(filename):
            raise IOError("Check path: %s"%filename, filename)

        with open(filename) as f:
            text = f.read()
            parser = bsdl.bsdlParser()
            ast = parser.parse(text, "bsdl_description", semantics=BsdlSemantics(), parseinfo=False)
            bsdldict = dict(ast.asjson())

        self.bsdl = bsdldict
        
        self.process_ioregs()
        
    def get_name(self):
        """Return the name of the device specified in the file"""
        return self.bsdl['component_name']
    
    def get_opcode(self, opcodename):
        """Return the opcode specified - normally one of 'SAMPLE', 'EXTEST', 'BYPASS'"""
        
        opcodes = self.bsdl['instruction_register_description']['instruction_opcodes']
        
        for opcode in opcodes:
            if opcode['instruction_name'].upper() == opcodename.upper():
                return opcode['opcode_list'][0]
        
        raise ValueError("Instruction %s not found in list: %s"%(opcodename, opcodes))
    
    def number_of_chainbits(self):
        """Get total number of bits in the scan chain"""
        
        return int(self.bsdl["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_length"])
        
    def process_ioregs(self, print_warnings=True):
        """Process the scan registers & build a dict we can use for input/output/oe access"""
    
        boundary_registers = self.bsdl["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_register"]
        
        io_regs = {}
        
        for d in boundary_registers:
            
            #Sometimes files have bad parse results - there is a good chance it's an internal
            #cell or something we don't need. So we just keep going.
            try:
                portid = d['cell_info']['cell_spec']['port_id']
            except TypeError:
                if print_warnings:
                    print("WARNING: skipping cell '%s' due to parse error"%d)
                continue
        
            if d['cell_info']['cell_spec']['function'] == 'INPUT':
                if portid not in io_regs:
                    io_regs[portid] = {}
            
                io_regs[portid]['input'] = int(d['cell_number'])
                
            if d['cell_info']['cell_spec']['function'] == 'OUTPUT':
                print("WARNING: Output-only cell detected - skipped")
                print(d)
                
            if d['cell_info']['cell_spec']['function'] == 'OUTPUT3':
                if portid not in io_regs:
                    io_regs[portid] = {}
                    
                io_regs[portid]['output'] = int(d['cell_number'])
                io_regs[portid]['oe'] = int(d['cell_info']['input_or_disable_spec']['control_cell'])
                io_regs[portid]['oe_disable'] = int(d['cell_info']['input_or_disable_spec']['disable_value'])
        
        self.io_regs = io_regs
    
    def get_idcode(self):
        """Extract idcode from BSDL file - returned as (mask, idcode)"""
        
        try:
            rawidcode = self.bsdl['optional_register_description']
            if isinstance(rawidcode, list):
                rawidcode = rawidcode[0] #TODO - cycle through extra registers, for now assume idcode one is first result
            rawidcode = rawidcode['idcode_register']
            
            #Maskbits seems to be first?
            maskbits = len(rawidcode[0])
            
            #Take rest and combine
            binstr = "".join(rawidcode[1:])
            baseid = int(binstr, 2)
            
            mask = int("1"*len(binstr), 2) #Mask is just how many valid bits are showing up
        except:
            print("Processing failed - debug info to help fix the code:")
            print("  optional_register_description: %s"%self.bsdl['optional_register_description'])
            print("  rawidcode at exception: %s"%rawidcode)
        
        return (mask, baseid)
    
    def pretty_dump(self):
        """Return an OK format string we can print to debug."""
        return json.dumps(self.bsdl, indent=1)