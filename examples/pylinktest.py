from jtagbs import jtagbs
from jtagbs.pylink import pylink

interface = pylink.PyLink()

jtag = jtagbs.JTAGBS(interface)

probes = jtag.list_available_probes()
print(probes)

jtag.open_probe('J-Link')
jtag.init_scanchain()

print(jtag.list_devids())
print(jtag.list_devices())

stm32 = jtag.get_device(1)