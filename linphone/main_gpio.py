import const
from pyA20.gpio import gpio
import time 
import linphone
import logging
import ConfigParser
import threading

logging.basicConfig(level=logging.INFO)

call_state_dict = {
    linphone.CallState.Idle: "Idle",
    linphone.CallState.IncomingReceived: "IncomingReceived",
    linphone.CallState.OutgoingInit: "OutgoingInit",
    linphone.CallState.OutgoingProgress: "OutgoingProgress",
    linphone.CallState.OutgoingRinging: "OutgoingRinging",
    linphone.CallState.OutgoingEarlyMedia: "OutgoingEarlyMedia",
    linphone.CallState.Connected: "Connected",
    linphone.CallState.StreamsRunning: "StreamsRunning",
    linphone.CallState.Pausing: "Pausing",
    linphone.CallState.Paused: "Paused",
    linphone.CallState.Resuming: "Resuming",
    linphone.CallState.Refered: "Refered",
    linphone.CallState.Error: "Error",
    linphone.CallState.End: "End",
    linphone.CallState.PausedByRemote: "PausedByRemote",
    linphone.CallState.UpdatedByRemote: "UpdatedByRemote",
    linphone.CallState.IncomingEarlyMedia: "IncomingEarlyMedia",
    linphone.CallState.Updating: "Updating",
    linphone.CallState.Released: "Released",
    linphone.CallState.EarlyUpdatedByRemote: "EarlyUpdatedByRemote",
    linphone.CallState.EarlyUpdating: "EarlyUpdating"
}

stream_params = {
    "Invalid":linphone.MediaDirection.Invalid,
    "Inactive":linphone.MediaDirection.Inactive,	 
    "SendOnly":linphone.MediaDirection.SendOnly,
    "RecvOnly":linphone.MediaDirection.RecvOnly,
    "SendRecv":linphone.MediaDirection.SendRecv
}

call_direction_dict = {
    linphone.MediaDirection.Invalid:"Invalid",
    linphone.MediaDirection.Inactive:"Inactive",	 
    linphone.MediaDirection.SendOnly:"SendOnly",
    linphone.MediaDirection.RecvOnly:"RecvOnly",
    linphone.MediaDirection.SendRecv:"SendRecv"
}

registration_state_dict = {
    "None":linphone.RegistrationState.None,
    "Progress":linphone.RegistrationState.Progress,
    "Ok":linphone.RegistrationState.Ok,
    "Cleared":linphone.RegistrationState.Cleared,
    "Failed":linphone.RegistrationState.Failed
}

configParser = ConfigParser.RawConfigParser()   
configFilePath = '/etc/voip/config'
configParser.read(configFilePath)

server_addr = configParser.get('linphone', 'server_addr')
snd_capture = configParser.get('linphone', 'snd_capture')
snd_playback= configParser.get('linphone', 'snd_playback') 
ring_tone_path= configParser.get('linphone', 'ring_tone_path')
lock = threading.Lock()

def log_handler(level, msg):
    method = getattr(logging, level)
    method(msg)

def enable_out_led(pi_id):
    gpio.output(const.pin_map[pi_id]["OUT"], 1)

def disable_out_led(pi_id):
    gpio.output(const.pin_map[pi_id]["OUT"], 0)

def disable_all_out_led():
    for pi_id in const.pin_map:
        gpio.output(const.pin_map[pi_id]["OUT"], 0)

def recall(pi_id):
    try:
        if not bool(gpio.input(const.pin_map[pi_id]["IN"])):
            # with lock:
            const.pin_map[pi_id]["OFF"] = True
    except Exception as e:
        logging.error(e)

def call_state_changed(core, call, state, message):
    try:
        logging.info("State Change {}: {} ".format( call.remote_address.username, call_state_dict[state]))
        if state == linphone.CallState.IncomingReceived:
            params = core.create_call_params(call)
            core.accept_call_with_params(call, params)
            logging.info("Receive a call from {}".format(call.remote_address.username))
            enable_out_led(call.remote_address.username[3])
        elif state == linphone.CallState.End:
            disable_out_led(call.remote_address.username[3])
        elif state == linphone.CallState.Error or state == linphone.CallState.Released:
            threading.Timer(10, recall, [call.remote_address.username[3]]).start()
        elif state == linphone.CallState.StreamsRunning:
            if len(core.calls) > 1:
                core.add_all_to_conference()
            pass
    except Exception as e:
        logging.error(e)

def registration_state_changed(core, proxy_config, state, message):
    logging.info("Login successfully")

def make_call(soft_phone_core, username):
    try:
        for call in soft_phone_core.calls:
            if call.remote_address.username == username:
                logging.info("There already a call with user: {}".format(username))
                return
        logging.info("Make a call to {}".format(username))
        params = soft_phone_core.create_call_params(None)
        soft_phone_core.invite_with_params('sip:{}@{}'.format(username, server_addr), params)
    except Exception as e:
        logging.error(e)

def terminate_call(soft_phone_core, username):
    try:
        logging.info("Terminated a call to {}".format(username))
        for current_call in soft_phone_core.calls:
            if current_call.remote_address.username == username:
                soft_phone_core.terminate_call(current_call)
    except Exception as e:
        logging.error(e)

def check_gpio(soft_phone_core):
    while True:
        if soft_phone_core.default_proxy_config.state == registration_state_dict["Ok"]:
            for pi_id in const.pin_map:
                if pi_id != const.pi_id:
                    pin_is_off = bool(gpio.input(const.pin_map[pi_id]["IN"]))
                    phone_is_off = const.pin_map[pi_id]["OFF"]
                    if pin_is_off and not phone_is_off:
                        # with lock:
                        const.pin_map[pi_id]["OFF"] = True
                        terminate_call(soft_phone_core, "100" + pi_id)
                    elif phone_is_off and not pin_is_off:
                        # with lock:
                        const.pin_map[pi_id]["OFF"] = False
                        make_call(soft_phone_core, "100" + pi_id)
                else:
                    # MIC enable
                    # with lock:
                    soft_phone_core.mic_enabled = not bool(gpio.input(const.pin_map[pi_id]["IN"]))

def main():
    try:
        """
        SETUP GPIO
        """
        gpio.init()
        for pi_id in const.pin_map:
            gpio.setcfg(const.pin_map[pi_id]["IN"], gpio.INPUT)
            gpio.pullup(const.pin_map[pi_id]["IN"], gpio.PULLUP)

            if pi_id != const.pi_id:
                gpio.setcfg(const.pin_map[pi_id]["OUT"], gpio.OUTPUT)
                gpio.output(const.pin_map[pi_id]["OUT"], 0)

        disable_all_out_led()

        """
        SETUP Linphone core
        """
        callbacks = {
            'call_state_changed': call_state_changed, 
            'registration_state_changed': registration_state_changed
        }
        # linphone.set_log_handler(log_handler)
        soft_phone_core = linphone.Core.new(callbacks, None, None)
        soft_phone_core.max_calls = 8
        if len(snd_capture):
            soft_phone_core.capture_device = snd_capture
        if len(snd_playback):
            soft_phone_core.playback_device = snd_playback
        soft_phone_core.keep_alive_enabled = True
        if len(ring_tone_path):
            soft_phone_core.ring = ring_tone_path
        # Configure sip account
        address = soft_phone_core.create_address('sip:{}@{}'.format(const.sip_username, server_addr))
        address.password = const.sip_password

        proxy_cfg = soft_phone_core.create_proxy_config()
        proxy_cfg.identity_address = address
        proxy_cfg.server_addr = 'sip:{};transport=udp'.format(server_addr)
        proxy_cfg.register_enabled = True

        auth_info = soft_phone_core.create_auth_info(const.sip_username, None, const.sip_password, None, None, server_addr)
        soft_phone_core.add_auth_info(auth_info)
        soft_phone_core.add_proxy_config(proxy_cfg)
        soft_phone_core.default_proxy_config = proxy_cfg
        thread_check_gpio = threading.Thread(target = check_gpio, args = (soft_phone_core, ))
        thread_check_gpio.start()

        while True: # Run forever
            soft_phone_core.iterate()
    except Exception as e:
        logging.error(e)

try:
    main()
except Exception as e:
        logging.error(e)