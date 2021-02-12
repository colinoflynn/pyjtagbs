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