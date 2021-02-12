from . import jlookup
import os

class JTAGBS(object):
    """JTAG Boundry Scan (JTAGBS) Top-Level Module - simply JTAG access to pins and stuff"""

    def __init__(self, interface):
        self.interface = interface


    def list_available_probes(self):
        """Returns string list of detected probes, index of string used to select a probe"""

        probes = self.interface.get_probe_names()

        return probes

    def open_probe(self, probe):
        """Opens a probe by index or name - name will match partial list"""

        if isinstance(probe, str):
            probenames = self.list_available_probes()

            id = None

            for i, avail in enumerate(probenames):
                if probe in avail:
                    id = probenames[avail]
            
            if id == None:
                raise ValueError("Did not find {} in available ({})".format(probe, probenames))

            probe = id

        self.interface.open_probe(probe)

    def init_scanchain(self):
        """Initialize the JTAG chain"""

        self.interface.scan_init_chain()

    def list_devids(self):
        """List detected device IDs"""

        numdev = self.interface.get_number_devices()

        devices = []

        for i in range(0, numdev):
            devices.append(self.interface.get_devid(i))

        return devices

    def list_devices(self):
        """List info about each part"""

        devices = self.list_devids()

        data = []

        for dev in devices:
            data.append(jlookup.j_lookup(dev))

        return data

    def get_device(self, device_index):
        """Return a Device() object of the given index, attached to this JTAG chain"""
        return Device(self, device_index)

    def scan(self):
        """Performs a scan, so updates register values"""
        self.interface.scan()

class Device(object):

    def __init__(self, jtag, device_index, autoscan=True):
        self.jtag = jtag
        self.bsdl = None
        self.autoscan = True
        self.mode = None
        self.deviceid = device_index

    def set_bsdl(self, filename):
        """Assign the given BSDL file to this device"""

        if not os.path.exists(filename):
            raise IOError("Check path: {}".format(filename), filename)

        filename = os.path.abspath(filename)

        self.jtag.interface.bsdl_attach(filename, self.deviceid)

        self.bsdl = filename

    def list_pins(self):
        """List known pins on the device"""

        if self.bsdl is None: raise AttributeError("This function requires a BSDL file be assigned")

        total_pins = self.jtag.interface.get_number_of_pins(self.deviceid)        

        pins = [self.jtag.interface.get_pin_properties(self.deviceid, pinid) for pinid in range(0, total_pins)]

        return pins

    def set_scan_mode(self, mode):
        """Set scan mode to active or passive"""
        self.mode = mode

        self.jtag.interface.set_scan_mode(self.deviceid, mode)

    def get_pin_state(self, pins):
        """Get state the device input pin(s).
        
        You can pass a list of pins, and each pin can be the pin name or index.
        If autoscan mode is on it will perform a scan before each return.
        """

        if self.autoscan:
            self.jtag.scan()

        delist = False

        if isinstance(pins, str) or isinstance(pins, int):
            pins = [pins]
            delist = True

        res = []

        for i in range(0, len(pins)):

            pin = pins[i]

            if isinstance(pin, str):
                pin = self.lookup_pinid(pin)

            res.append(self.jtag.interface.get_pin_state(self.deviceid, pin))

        if delist:
            return res[0]
        else:
            return res

    def set_pin_state(self, pins, states, checkmode=True):
        """Set the output pin state(s). Must be in 'active' mode.

        You can pass a list of pins, and each pin can be the pin name or index.
        If autoscan mode is on it will perform a scan to set the output.
        Pins can be 'True', 'False', or 'None' (High-Z)
        """

        if checkmode:
            if self.mode != "active" and self.mode != "extest":
                raise IOError("Set chain to 'active' mode")

        if isinstance(pins, str) or isinstance(pins, int):
            pins = [pins]
            states = [states]

        for i in range(0, len(pins)):

            pin = pins[i]
            state = states[i]

            if isinstance(pin, str):
                pin = self.lookup_pinid(pin)

            state = self.lookup_pinstate(state)

            if state is True or state is False:
                self.jtag.interface.set_pin_state(self.deviceid, pin, True, "oe")
            else:
                self.jtag.interface.set_pin_state(self.deviceid, pin, False, "oe")

            if state is None:
                state = False

            self.jtag.interface.set_pin_state(self.deviceid, pin, state, "output")

        if self.autoscan:
            self.jtag.scan()

    def lookup_pinid(self, pinname):

        if self.bsdl is None: raise AttributeError("This function requires a BSDL file be assigned")

        #TODO - we should probably cache this... not sure what lib does on each call, might be intense
        pins = self.list_pins()

        idx = None

        for i,pin in enumerate(pins):
            if pinname == pin['name']:
                idx = i
                break

        if idx is None:
            for i,pin in enumerate(pins):
                if pinname in pin['name']:
                    if idx is not None:
                        raise ValueError("Ambigious match on {}".format(pinname))
                    idx = i

        if idx is None:
            raise ValueError("Pin name {} not found".format(pinname))                     

        return idx

    def lookup_pinstate(self, pinstate):

        if pinstate == "low" or pinstate == 0 or pinstate == False:
            return False

        elif pinstate == "high" or pinstate == 1 or pinstate == True:
            return True

        elif pinstate == "high-z" or pinstate == "highz" or pinstate == -1 or pinstate == None:
            return None
