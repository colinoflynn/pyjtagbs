# Python JTAG Boundry Scan (pyjtagbs)

*If you've tried to get boundary scan working under Python, you'll truely appreciate the name pyjtagbs.*

This is a thin wrapper on a very nice library currenting, giving you simple Python access to JTAG boundry scan pins.

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

## 'JTAG Boundary Scanner' Tool & Library

100% of the actual work is done by the amazing JTAG Boundary Scanner tool available at https://github.com/viveris/jtag-boundary-scanner.

That library was developed by Viveris (credit to Jean-François DEL NERO & Sébastien Corbeau).

**WARNING: The .dll in the repo is only a 32-bit build, so this only works with 32-bit Python on Windows**

This library supports FTDI cables along with Segger J-Link tools.

### Using J-Link

The device can use a J-Link, it needs Segger's DLL as well for that. For some reason the J-Link DLL needs to be at the same location as your file that is running from (to be fixed), so to run 'example.py' you need the DLL in that folder as well (or install the DLL to your Windows system path - which may be dangerous as other tools will find that version).

## More JTAG Features

Future work may support other backends - some of the features (such as BSDL parsing) required are available in Python implementations already. However having SPI & I2C access is nice with the speed of the compiled C library.

## Other Tools worth Mentioning

* urJTAG - open source JTAG tooling, the original!
* TopJTAG - low-cost ($100) with GUI that shows each pin on the package itself - very handy for debug.

## GUI

For a GUI, see the https://github.com/viveris/jtag-boundary-scanner which offers a nice GUI interface to view each pin state.

## BSDL Sources

BSDL files are found around the web. For ST devices, see the "CAD Resources" tab, i.e.: https://www.st.com/en/microcontrollers-microprocessors/stm32f405og.html#cad-resources

## JTAG Notes

Some devices have JTAG that is shared between debug & boundry scan by a physical pin (for example - Microchip SAM3U). For these devices your board is likely configured only for debug access, you may need to cahgne a pin strap or similar.