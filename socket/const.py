from pyA20.gpio import port
import socket

phone_id = socket.gethostname()

list_phone = {
    "OrangePi1": {
        "IN": port.PA10,
        "OUT": port.PA3,
        "state": False,
        "addr": ("localhost", 8058)
    },
    "OrangePi2": {
        "IN": port.PA13,
        "OUT": port.PA0,
        "state": False,
        "addr": ("localhost", 8058)
    },
    "OrangePi3": {
        "IN": port.PA14,
        "OUT": port.PA7,
        "state": False,
        "addr": ("localhost", 8058)
    },
    "OrangePi4": {
        "IN": port.PA2,
        "OUT": port.PA1,
        "state": False,
        "addr": ("localhost", 8058)
    },
    "OrangePi5": {
        "IN": port.PA16,
        "OUT": port.PG7,
        "state": False,
        "addr": ("localhost", 8058)
    },
    "OrangePi6": {
        "IN": port.PA15,
        "OUT": port.PG6,
        "state": False,
        "addr": ("localhost", 8058)
    },
    "OrangePi7": {
        "IN": port.PA18,
        "OUT": port.PA6,
        "state": False,
        "addr": ("localhost", 8058)
    },
    "OrangePi8": {
        "IN": port.PA19,
        "OUT": port.PA11,
        "state": False,
        "addr": ("localhost", 8058)
    }
}

pin_mic = port.PA12
