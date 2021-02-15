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
        
    def name(self):
        """Returnt the name of the device"""
        return self.bsdl['component_name']
    
    def opcode(self, opcodename):
        """Return the opcode specified"""
        
        opcodes = self.bsdl['instruction_register_description']['instruction_opcodes']
        
        for opcode in opcodes:
            if opcode['instruction_name'].upper() == opcodename.upper():
                return opcode['opcode_list'][0]
        
        raise ValueError("Instruction %s not found in list: %s"%(opcodename, opcodes))
    
    def number_of_chainbits(self):
        
        return int(self.bsdl["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_length"])
        
    def process_ioregs(self):
    
        boundary_registers = self.bsdl["boundary_scan_register_description"]["fixed_boundary_stmts"]["boundary_register"]
        
        io_regs = {}
        
        for d in boundary_registers:
            portid = d['cell_info']['cell_spec']['port_id']
        
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
    
    def pretty_dump(self):
        return json.dumps(self.bsdl, indent=1)