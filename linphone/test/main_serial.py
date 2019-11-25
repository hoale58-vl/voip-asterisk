from softphone import SoftPhone
import time
from pySerial import PySerial
import re
import threading
import logging

logging.basicConfig(level=logging.DEBUG)

sip_username = "1001"
sip_password = "lvhoa581995"
conference_dial = "4000"

soft_phone = SoftPhone(sip_username, sip_password)
py_serial = PySerial()

linphoneThread = threading.Thread(target=soft_phone.run, args=())
linphoneThread.daemon = True
linphoneThread.start()

def debug():
    while True:
        logging.debug('Login: %r, InCall: %r' %(soft_phone.login, soft_phone.is_in_call()))
        time.sleep(5)
debugThread = threading.Thread(target=debug, args=())
debugThread.daemon = True
debugThread.start()

try:
    while True:
        if soft_phone.login and not soft_phone.is_in_call():
            res = soft_phone.make_call(conference_dial)

        line = py_serial.readline()
        if re.match('enter', line, re.IGNORECASE ) and not soft_phone.is_in_call():
            res = soft_phone.make_call(conference_dial)
        elif re.match('exit', line, re.IGNORECASE ) and soft_phone.is_in_call():
            soft_phone.stop_all_call()
except KeyboardInterrupt:
    linphoneThread.join()
    debugThread.join()
