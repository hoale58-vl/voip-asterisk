import socket 
from audio import InputAudio
from thread import start_new_thread
from gpio import GpioControl

# GPIO THread
gpioControl = GpioControl()
gpioThread = threading.Thread(target=gpioControl.check_input, args=())
gpioThread.daemon = True
gpioThread.start()

class AudioUdpServer:
    def __init__(self, ip_addr='0.0.0.0', port=8058):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) 
        self.server.setblocking(False)
        self.server.bind((ip_addr, port))
        self.inputMic = InputAudio()
        self.outputSpeaker = OutPutAudio()

    def close(self):
        self.server.close() 

    def run(self):
        start_new_thread(self.receivThread,()) 
        while True: 
            try:
                rawData = self.inputMic.record()
                for phone in gpioControl.list_phone:
                    if gpioControl.list_phone[phone]["state"]:
                        self.server.sendto(rawData, gpioControl.list_phone[phone]["addr"])
            except Exception as e: 
                print(e)
                continue

    def receivThread(self): 
        while True: 
            try: 
                message, addr = self.server.recvfrom(4096) 
                if message:
                    self.outputSpeaker.play(message) 
            except Exception as e: 
                print(e)
                continue