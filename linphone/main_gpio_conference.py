import const
from pyA20.gpio import gpio, port
import time 
import linphone
import logging
import ConfigParser
import socket
from threading import Thread, Lock
import re
import os

wav_file = "/usr/share/sounds/linphone/rings/toy-mono.wav"

logging.basicConfig(level=logging.INFO)

pin_map = {
    "1": {
        "IN": port.PA10,
        "OUT": port.PA3,
        "OFF": True
    },
    "2": {
        "IN": port.PA13,
        "OUT": port.PA0,
        "OFF": True
    },
    "3": {
        "IN": port.PA14,
        "OUT": port.PA7,
        "OFF": True
    },
    "4": {
        "IN": port.PA2,
        "OUT": port.PA1,
        "OFF": True
    },
    "5": {
        "IN": port.PA16,
        "OUT": port.PG7,
        "OFF": True
    },
    "6": {
        "IN": port.PA15,
        "OUT": port.PG6,
        "OFF": True
    },
    "7": {
        "IN": port.PA18,
        "OUT": port.PA6,
        "OFF": True
    },
    "8": {
        "IN": port.PA19,
        "OUT": port.PA11,
        "OFF": True
    }
}

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

UDP_PORT = 8558
bufferSize  = 1024
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(("0.0.0.0", UDP_PORT))
lock = Lock()

def log_handler(level, msg):
    method = getattr(logging, level)
    method(msg)

def trigger_out_led(pi_id, enable):
    global pin_map
    if (gpio.input(pin_map[pi_id]["OUT"]) == 1) == enable:
        return False
    with lock:
        gpio.output(pin_map[pi_id]["OUT"], 1 if enable else 0)
    return True

def disable_all_out_led():
    for pi_id in pin_map:
        gpio.output(pin_map[pi_id]["OUT"], 0)

def call_state_changed(core, call, state, message):
    try:
        logging.info("State Change {}: {} ".format( call.remote_address.username, call_state_dict[state]))
        if state == linphone.CallState.Released:
            make_call(core, "4001")
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

def listen_udp():
    global pin_map
    global server_socket
    logging.info("UDP server up and listening")
    while(True):
        try:
            bytesAddressPair = server_socket.recvfrom(bufferSize)
            message = bytesAddressPair[0].decode("utf-8") 
            address = bytesAddressPair[1]
            matched = re.match(r'(\d) (is|was) (on|off)', message)
            if matched:
                if matched.group(2) == "is":
                    if (trigger_out_led(matched.group(1), matched.group(3) == "on")):
                        logging.info("Receive UDP message: {}".format(message))
                        msgFromClient       = "{} was {}".format(const.pi_id, matched.group(3))
                        bytesToSend         = str.encode(msgFromClient)
                        with lock:
                            server_socket.sendto(bytesToSend, ("192.168.7.10{}".format(matched.group(1)), UDP_PORT))
                elif matched.group(2) == "was":
                    if matched.group(3) == "on":
                        with lock:
                            pin_map[matched.group(1)]["OFF"] = False
                    else:
                        with lock:
                            pin_map[matched.group(1)]["OFF"] = True
            else:
                logging.info("Receive UDP message: Wrong format - {}".format(message))
        except Exception as e:
            logging.error(e)

def main():
    try:
        """
        SETUP GPIO
        """
        gpio.init()
        for pi_id in pin_map:
            gpio.setcfg(pin_map[pi_id]["IN"], gpio.INPUT)
            gpio.pullup(pin_map[pi_id]["IN"], gpio.PULLUP)

            if pi_id != const.pi_id:
                gpio.setcfg(pin_map[pi_id]["OUT"], gpio.OUTPUT)
                gpio.output(pin_map[pi_id]["OUT"], 0)

        disable_all_out_led()

        """
        SETUP Linphone core
        """
        callbacks = {
            'call_state_changed': call_state_changed, 
            'registration_state_changed': registration_state_changed,
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

        t = Thread(target=listen_udp, args=())
        t.start()

        soft_phone_core.mic_enabled = False
        os.system("/usr/bin/aplay " + wav_file)
        while True: # Run forever
            soft_phone_core.iterate()
            if soft_phone_core.default_proxy_config.state == registration_state_dict["Ok"]:
                if not soft_phone_core.in_call():
                    make_call(soft_phone_core, "4001")
                    
                for pi_id in pin_map:
                    if pi_id != const.pi_id:
                        pin_is_off = bool(gpio.input(pin_map[pi_id]["IN"]))
                        phone_is_off = pin_map[pi_id]["OFF"]
                        if pin_is_off and not phone_is_off:
                            msgFromClient       = "{} is off".format(const.pi_id)
                            bytesToSend         = str.encode(msgFromClient)
                            with lock:
                                server_socket.sendto(bytesToSend, ("192.168.7.10{}".format(pi_id), UDP_PORT))
                        elif phone_is_off and not pin_is_off:
                            msgFromClient       = "{} is on".format(const.pi_id)
                            bytesToSend         = str.encode(msgFromClient)
                            with lock:
                                server_socket.sendto(bytesToSend, ("192.168.7.10{}".format(pi_id), UDP_PORT))
                    else:
                        # MIC enable
                        pin_is_off = bool(gpio.input(pin_map[pi_id]["IN"]))
                        phone_is_off = pin_map[pi_id]["OFF"]
                        if pin_is_off and not phone_is_off:
                            with lock:
                                pin_map[pi_id]["OFF"] = True
                            soft_phone_core.mic_enabled = False
                        elif phone_is_off and not pin_is_off:
                            with lock:
                                pin_map[pi_id]["OFF"] = False
                            soft_phone_core.mic_enabled = True
    except Exception as e:
        logging.error(e)

try:
    main()
except Exception as e:
        logging.error(e)