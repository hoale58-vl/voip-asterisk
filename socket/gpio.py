import const
from pyA20.gpio import gpio
from pyA20.gpio import connector

gpio.init()

class GpioControl:
    def __init__(self):
        self.setup = False
        self.list_phone = const.list_phone
        self.stop = False
        self.mute = False

        self.phone_id = const.phone_id

        for phone in self.list_phone:
            if phone != self.phone_id:
                self.list_phone[phone]["state"] = False
                self.list_phone[phone]["trigger"] = True
                gpio.setcfg(self.list_phone[phone]["OUT"], gpio.OUTPUT)
                gpio.setcfg(self.list_phone[phone]["IN"], gpio.INPUT)
                gpio.pullup(self.list_phone[phone]["IN"], gpio.PULLUP)
                gpio.output(self.list_phone[phone]["OUT"], 1)

        gpio.setcfg(const.pin_mic, gpio.INPUT)
        gpio.pullup(const.pin_mic, gpio.PULLUP)
        self.setup = True

    def check_input(self):
        while not self.stop and self.setup: # Run forever
            for phone in self.list_phone: 
                if phone != self.phone_id:
                    state = not bool(gpio.input(self.list_phone[phone]["IN"]))
                    self.list_phone[phone]["trigger"] = (self.list_phone[phone]["state"] is not state)
                    self.list_phone[phone]["state"] = state
            self.mute = not bool(const.pin_mic)
                        
    def set_led(self, phone, enable):
        if self.setup:
            if enable:
                gpio.output(self.list_phone[phone]["OUT"], 0)
            else:
                gpio.output(self.list_phone[phone]["OUT"], 1)
