import serial
import logging
import signal

class PySerial:
	def __init__(self, port='/dev/serial0', baudrate=115200, timeout=1):
		self.ser = serial.Serial(
			port = port,
			baudrate = baudrate,
			parity = serial.PARITY_NONE,
			stopbits = serial.STOPBITS_ONE,
			bytesize = serial.EIGHTBITS,
			timeout = timeout
		)
		logging.basicConfig(level=logging.INFO)
		signal.signal(signal.SIGINT, self.signal_handler)

	def readline(self):
		line = self.ser.readline()
		self.ser.write(line)
		return line

	def close(self):
		self.ser.close()

	def status(self):
		self.ser.is_open()

	def signal_handler(self, signal, frame):
		self.close()