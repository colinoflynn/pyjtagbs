import json
import sys

from jtagbs import jtagbs
from jtagbs.pylinkbs import pylinkbs

interface = pylinkbs.PyLinkRawBS()

jtag = jtagbs.JTAGBS(interface)

probes = jtag.list_available_probes()
print(probes)

jtag.open_probe('J-Link')
jtag.init_scanchain()

print(jtag.list_devids())
print(jtag.list_devices())

stm32 = jtag.get_device(1)

#stm32.set_bsdl(r"../bsdl_files/st/stm32f4/STM32F405_415_407_417_LQFP64.bsd")
stm32.set_bsdl(r"../bsdl_files/xilinx/xc6slx9_tqg144.bsd")