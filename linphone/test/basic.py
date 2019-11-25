import linphone
import logging
import sys


def main():
    logging.basicConfig(level=logging.INFO)

    def log_handler(level, msg):
        method = getattr(logging, level)
        method(msg)

    def global_state_changed(*args, **kwargs):
        logging.warning("global_state_changed: %r %r" % (args, kwargs))

    def registration_state_changed(core, call, state, message):
        logging.warning("registration_state_changed: " + str(state) + ", " + message)

    callbacks = {
        'global_state_changed': global_state_changed,
        'registration_state_changed': registration_state_changed,
    }

    linphone.set_log_handler(log_handler)
    core = linphone.Core.new(callbacks, None, None)
    proxy_cfg = core.create_proxy_config()
    proxy_cfg.identity_address = core.create_address("sip:1001@192.168.3.129")
    proxy_cfg.server_addr = "sip:192.168.3.129"
    proxy_cfg.register_enabled = False
    core.add_proxy_config(proxy_cfg)
    while True:
        core.iterate()

main()