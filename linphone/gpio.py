import const
from pyA20.gpio import gpio
from pyA20.gpio import connector

gpio.init()

class GpioControl:
    def __init__(self, pi_id):
        self.setup = False
        self.list_phone = {}
        self.stop = False
        self.mute = False

        self.pi_id = pi_id

        for pi_id in const.pin_map:
            if pi_id != self.pi_id:
                self.list_phone[pi_id] = {}
                self.list_phone[pi_id]["state"] = False
                self.list_phone[pi_id]["trigger"] = True
                gpio.setcfg(const.pin_map[pi_id]["OUT"], gpio.OUTPUT)
                gpio.setcfg(const.pin_map[pi_id]["IN"], gpio.INPUT)
                gpio.pullup(const.pin_map[pi_id]["IN"], gpio.PULLUP)
                gpio.output(const.pin_map[pi_id]["OUT"], 1)

        gpio.setcfg(const.pin_mic, gpio.INPUT)
        gpio.pullup(const.pin_mic, gpio.PULLUP)
        self.setup = True

    def check_input(self):
        while not self.stop and self.setup: # Run forever
            for pi_id in const.pin_map: 
                if pi_id != self.pi_id:
                    state = not bool(gpio.input(const.pin_map[pi_id]["IN"]))
                    self.list_phone[pi_id]["trigger"] = (self.list_phone[pi_id]["state"] is not state)
                    self.list_phone[pi_id]["state"] = state
            self.mute = not bool(const.pin_mic)
                        
    def set_led(self, pi_id, enable):
        if self.setup:
            if enable:
                gpio.output(const.pin_map[pi_id]["OUT"], 0)
            else:
                gpio.output(const.pin_map[pi_id]["OUT"], 1)

    def debug_list_phone(self):
        result = ''
        for phone in self.list_phone:
            if self.list_phone[phone]["trigger"]:
                result = ('Phone at %s has new state %r,' %(phone, self.list_phone[phone]["state"]))
        return result