# JTAG with the BS (Boundary Scan) - pyjtagbs

*If you've tried to get boundary scan working under Python, you'll truly appreciate the name pyjtagbs.*

This is a thin wrapper on a very nice library currently, giving you simple Python access to JTAG Boundary Scan pins. Future work will implement some features in native Python (most of it already exists in other libraries).

```
from jtagbs import JTAGCore, JTAGBS

interface = JTAGCore()
jtag = JTAGBS(interface)

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

### Using ChipWhisperer Husky

The Python library can be imported into your Jupyter notebooks for use with a ChipWhisperer-Husky/Husky-Plus. This gives you JTAG access from the 20-pin "UserIO" front panel connectors.

You can then wire some of those pins to also be used for triggering. See the ChipWhisperer jupyter notebooks for examples.

### Using J-Link

The device can use a J-Link, it needs Segger's DLL as well for that. For some reason the J-Link DLL needs to be at the same location as your file that is running from (to be fixed), so to run 'example.py' you need the DLL in that folder as well (or install the DLL to your Windows system path - which may be dangerous as other tools will find that version).

## More JTAG Features

Future work may support other backends - some of the features (such as BSDL parsing) required are available in Python implementations already. However having SPI & I2C access is nice with the speed of the compiled C library.

### PyLink Interface

The initial "other backend" is the PyLink interface.

## Other Tools Worth Mentioning

* urJTAG - open source JTAG tooling, the original!
* ~~TopJTAG - low-cost ($100) with GUI that shows each pin on the package itself~~ Reported as of Aug/2023 that this is a dead project, I have been unable to get in touch with owner for past year so unfortunutly cannot recommend it.

## GUI

For a GUI, see the https://github.com/viveris/jtag-boundary-scanner which offers a nice GUI interface to view each pin state.

## BSDL Sources

BSDL files are found around the web. For ST devices, see the "CAD Resources" tab, i.e.: https://www.st.com/en/microcontrollers-microprocessors/stm32f405og.html#cad-resources

## JTAG Notes

Some devices have JTAG that is shared between debug & boundary scan by a physical pin (for example - Microchip SAM3U). For these devices your board is likely configured only for debug access, you may need to change a pin strap or similar.
