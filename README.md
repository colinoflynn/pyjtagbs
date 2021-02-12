# Python JTAG Boundry Scan (pyjtagbs)

*If you've tried to get boundary scan working under Python, you'll truely appreciate the name pyjtagbs.*

```
import pyjtagbs

jtag = pyjtagbs()

probes = jtag.list_available_probes()

print(probes)

jtag.open_probe_by_name('JLINK')

jtag.init_scanchain()

jtag.list_devids()

device = jtag.get_device(1)

device.set_bsdl(xxxxxxxxxx)

device.list_pins()

device.set_scan_mode("passive")

device.get_pin_state("PA11")

device.get_pin_state(["PA11", "PA12"])

device.set_scan_mode("active")

device.set_pin_state("PA12", True)

device.set_pin_state(["PA11, "PA12"], [True, False])

spi = device.spi(clk="PA11", copi="PA12", cipo="PA13", cs="PA14")

```

## Library Dependancy

This tool currently uses the amazing JTAG Boundary Scanner tool. 

## Other Tools worth Mentioning

* urJTAG
* TopJTAG

## GUI

## BDSL Sources
