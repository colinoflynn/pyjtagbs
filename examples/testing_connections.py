from jtagbs import jtagbs
from jtagbs.viveris import jtagcore

interface = jtagcore.JTAGCore()
jtag = jtagbs.JTAGBS(interface)

probes = jtag.list_available_probes()

jtag.open_probe('JLINK')
jtag.init_scanchain()

devices = jtag.list_devices()
for i, dev in enumerate(devices):
    print("Device {} is from {}".format(i, dev['manufacturer']))

s6lx9 = jtag.get_device(0)
arm = jtag.get_device(1)
stm32 = jtag.get_device(2)

s6lx9.set_bsdl(r"../bsdl_files/xilinx/xc6slx9l_tqg144.bsd")
arm.set_bsdl(r"../bsdl_files/st/stm32f4/CortexMx.bsd")
stm32.set_bsdl(r"../bsdl_files/st/stm32f4/STM32F405_415_407_417_LQFP64.bsd")

stm32pins = stm32.list_pins()
s6lx9pins = s6lx9.list_pins()

print("STM32 Pins")
stm32io = []
for p in stm32pins:
    if 'input' and 'output' in p['type']: stm32io.append(p['name'])
print(stm32io)

print("S6LX9 Pins")
s6lx9io = []
for p in s6lx9pins:
    if 'input' and 'output' in p['type']: s6lx9io.append(p['name'])
print(s6lx9io)

s6lx9testpins = [80, 81, 82, 83, 84, 85, 87, 88, 92, 93, 94, 95, 111, 112, 114, 115, 116, 117, 118, 119, 120]
s6lx9testpins = ['IO_P%d'%p for p in s6lx9testpins]

stm32testpins = ['PA9', 'PA10', 'PA11', 'PA12', 'PB13', 'PB14', 'PB15', 'PB12', 'PC0', 'PC1', 'PC2', 'PC3', 'PC13', 'PC14', 'PC15']

s6lx9.set_scan_mode('passive')
stm32.set_scan_mode('active')

base_pin_state = s6lx9.get_pin_state(s6lx9testpins)
#print(base_pin_state.count(1))
print(s6lx9.get_pin_state('IO_P81'))
for p in stm32testpins:
    stm32.set_pin_state(stm32testpins, ['high-z']*len(stm32testpins))
    stm32.set_pin_state(p, True)
    
    new_pin_state = s6lx9.get_pin_state(s6lx9testpins)   
    print(new_pin_state)

stm32.set_pin_state(stm32testpins, ['high-z']*len(stm32testpins))