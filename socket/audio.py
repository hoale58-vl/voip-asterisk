import pyaudio

class OutPutAudio:
    def __init__(self,
            form_1 = pyaudio.paInt16, # 16-bit resolution
            chans = 1, # 1 channel
            samp_rate = 44100, # 44.1kHz sampling rate
            dev_index = 0 # device index found by p.get_device_info_by_index(ii)
            ):
        self.audio = pyaudio.PyAudio() # create pyaudio instantiation
        self.stream = self.audio.open(format = form_1,
                    rate = samp_rate,
                    channels = chans, \
                    input_device_index = dev_index,
                    output = True)
    
    def play(self, data):
        self.stream.write(data)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

class InputAudio:
    def __init__(self,
            form_1 = pyaudio.paInt16, # 16-bit resolution
            chans = 1, # 1 channel
            samp_rate = 44100, # 44.1kHz sampling rate
            chunk = 4096, # 2^12 samples for buffer
            dev_index = 0 # device index found by p.get_device_info_by_index(ii)
            ):
        self.audio = pyaudio.PyAudio() # create pyaudio instantiation
        self.stream = self.audio.open(format = form_1,
                    rate = samp_rate,
                    channels = chans, \
                    input_device_index = dev_index,
                    input = True, \
                    frames_per_buffer=chunk)
        self.chunk = chunk
    
    def record(self):
        return self.stream.read(self.chunk)

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()