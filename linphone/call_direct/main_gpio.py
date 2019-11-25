from softphone import SoftPhone, call_state_dict, call_direction_dict
import time
import re
import threading
import logging
import const
from gpio import GpioControl
logging.basicConfig(level=logging.DEBUG)

# Linphone thread
soft_phone = SoftPhone(const.sip_username, const.sip_password)
linphoneThread = threading.Thread(target=soft_phone.run, args=())
linphoneThread.daemon = True
linphoneThread.start()

# GPIO THread
gpioControl = GpioControl(const.pi_id)
gpioThread = threading.Thread(target=gpioControl.check_input, args=())
gpioThread.daemon = True
gpioThread.start()

# Debug Thread
running = True
def debug():
    while running:
        logging.debug('Login: %r, List Call:' %(soft_phone.login))
        for call in soft_phone.get_calls():
            print('Call %s: State %s, Direction %s' %(call.remote_address.username, call_state_dict[call.state], call_direction_dict[call.current_params.audio_direction]))
            print('')
        time.sleep(5)
debugThread = threading.Thread(target=debug, args=())
debugThread.daemon = True
debugThread.start()

try:
    join_rooms = False
    soft_phone.core.mic_enabled = True

    while running:
        #  Check state
        if soft_phone.login:
            for phone_id in gpioControl.list_phone:
                soft_phone.update_call("100" + phone_id, gpioControl.list_phone[phone_id]["state"])
        
        if gpioControl.mute and soft_phone.core.mic_enabled:
            soft_phone.core.mic_enabled = False
        elif not gpioControl.mute and not soft_phone.core.mic_enabled:
            soft_phone.core.mic_enabled = True
except KeyboardInterrupt:
    linphone.quit = True
    linphoneThread.join()

    running = False
    debugThread.join()

    gpioControl.stop = True
    gpioThread.join()
