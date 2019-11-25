import time
import linphone
import logging
import signal
import re
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

class SoftPhone:
    def __init__(self, 
                username, 
                password, 
                server_addr='192.168.2.131', 
                protocol='udp', 
                snd_capture='', 
                snd_playback='', 
                ring_tone_path=''
            ):
        self.quit = False

        # Callback funcs
        callbacks = {
                    'call_state_changed': self.call_state_changed, 
                    'registration_state_changed': self.registration_state_changed
                    }
        
        # Configure the linphone core
        logging.basicConfig(level=logging.INFO)
        signal.signal(signal.SIGINT, self.signal_handler)
        # linphone.set_log_handler(self.log_handler)
        self.core = linphone.Core.new(callbacks, None, None)
        # self.core.migrate_to_multi_transport()
        self.core.max_calls = 8
        if len(snd_capture):
            self.core.capture_device = snd_capture
        if len(snd_playback):
            self.core.playback_device = snd_playback
        self.core.keep_alive_enabled = True
        if len(ring_tone_path):
            self.core.ring = ring_tone_path

        # Configure sip account
        self.login = False
        self.server_addr = server_addr
        self.address = self.core.create_address('sip:{}@{}'.format(username, server_addr))
        proxy_cfg = self.core.create_proxy_config()
        proxy_cfg.identity_address = self.address
        proxy_cfg.server_addr = 'sip:{};transport={}'.format(server_addr, protocol)
        proxy_cfg.register_enabled = True
        proxy_cfg.publish_enabled = True
        self.core.add_proxy_config(proxy_cfg)
        self.core.default_proxy_config = proxy_cfg
        auth_info = self.core.create_auth_info(username, None, password, None, None, server_addr)
        self.core.add_auth_info(auth_info)
        logging.info('Linphone setup user {} done.'.format(username))

    def registration_state_changed(self, core, proxy_config, state, message):
        logging.info("Registration State Changed: %d %s" % (state, message))
        self.login = (state == registration_state_dict["Ok"])

    def call_state_changed(self, core, call, state, message):
        print(call_state_dict[state], message, call.reason)
        if state == linphone.CallState.Paused:
            print("resume ne")
            # self.core.resume_call(call)
        elif state == linphone.CallState.Error:
            print("Call Error: ", call.error_info.details, message)

    def make_call(self, username, is_my_id):
        # If call is Exists in list call
        for current_call in self.core.calls:
            if current_call.remote_address.username == username:
                return None
        
        logging.info('Calling {}'.format(username))
        params = self.core.create_call_params(None)
        if is_my_id:
            # My Room - RecvOnly
            params.audio_direction = stream_params["SendOnly"]
        else:
            # Other Room
            params.audio_direction = stream_params["SendOnly"]
        call = self.core.invite_with_params('sip:{}@{}'.format(username, self.server_addr), params)
        # self.core.add_to_conference(call)
        return call

    # Update other call
    def update_call(self, username, enable):
        for current_call in self.core.calls:
            if current_call.remote_address.username == username:
                # print(username, enable, call_state_dict[current_call.state])
                # Existed and Enable -> OK No change
                # Existed but Disable -> Terminated it
                if not enable:
                    self.core.terminate_call(current_call)
                return
        
        # Not existed and Enable -> Make a Call
        if enable:
            self.make_call(username, False)

    def signal_handler(self, signal, frame):
        self.core.terminate_all_calls()
        self.quit = True

    def log_handler(self, level, msg):
        method = getattr(logging, level)
        method(msg)

    def run(self):
        while not self.quit:
            self.core.iterate()
            time.sleep(0.03)

    def get_calls(self):
        return self.core.calls
