import socket
from pyA20.gpio import port
import re

no_of_pi = 8

pi_id = re.match(r"OrangePi(\d)", socket.gethostname()).group(1)
sip_username = "100" + pi_id
sip_password = "lvhoa581995"
conference_dial = "400"

pin_map = {
    "1": {
        "IN": port.PA10,
        "OUT": port.PA3,
    },
    "2": {
        "IN": port.PA13,
        "OUT": port.PA0,
    },
    "3": {
        "IN": port.PA14,
        "OUT": port.PA7,
    },
    "4": {
        "IN": port.PA2,
        "OUT": port.PA1,
    },
    "5": {
        "IN": port.PA16,
        "OUT": port.PG7,
    },
    "6": {
        "IN": port.PA15,
        "OUT": port.PG6,
    },
    "7": {
        "IN": port.PA18,
        "OUT": port.PA6,
    },
    "8": {
        "IN": port.PA19,
        "OUT": port.PA11,
    }
}

pin_mic = port.PA12

