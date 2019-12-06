import socket
import re

pi_id = re.match(r"Pi(\d)", socket.gethostname()).group(1)
sip_username = "100" + pi_id
sip_password = "lvhoa581995"



