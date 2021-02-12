# Python JTAG Boundry Scan (pyjtagbs)

*If you've tried to get boundary scan working under Python, you'll truely appreciate the name pyjtagbs.*

This is a think wrapper on a very nice library, but gives you simple Python access.

```
from jtagbs import jtagbs
from jtagbs.viveris import jtagcore

interface = jtagcore.JTAGCore()
jtag = jtagbs.JTAGBS(interface)

probes = jtag.list_available_probes()
print(probes)

jtag.open_probe('JLINK')
jtag.init_scanchain()

print(jtag.list_devids())
print(jtag.list_devices())

stm32 = jtag.get_device(1)

stm32.set_bsdl(r"bsdl_files/st/stm32f4/STM32F405_415_407_417_LQFP64.bsd")

print(stm32.list_pins())

print(stm32.get_pin_state("PC2"))
print(stm32.get_pin_state(["PC2", "PC1"]))

stm32.set_scan_mode("active")

stm32.set_pin_state("PC15", True)
stm32.set_pin_state("PC14", True)

stm32.set_pin_state(["PC15", "PC14"], [True, False])

stm32.set_pin_state(["PC15", "PC14"], [None, None])

#spi = device.spi(clk="PA11", copi="PA12", cipo="PA13", cs="PA14")

```

## Library Dependancy

100% of the actual work is done by the amazing JTAG Boundary Scanner tool available at https://github.com/viveris/jtag-boundary-scanner.

That library was developed by Viveris (credit to Jean-François DEL NERO & Sébastien Corbeau).

**WARNING: The .dll in the repo is only a 32-bit build, so this only works with 32-bit Python on Windows**

### Using J-Link

The device can use a J-Link, it needs Segger's DLL as well for that.

## Other Tools worth Mentioning

* urJTAG
* TopJTAG

## GUI

## BDSL Sources
