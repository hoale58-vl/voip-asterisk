#include <alsa/asoundlib.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <ctype.h>
#include <sched.h>
#include <stdio.h>
#include <vector>
#include <wiringPi.h>
#include <netdb.h>

#define logMessage printf
#define PACKETSIZE 16384
#define UDP_PORT 2305

void setScheduler();
void setHwParams(snd_pcm_t *hWave, int numChannels, int bytesPerSample, int samplePerSec, int period, int numBuffer);
void dumpParams(snd_pcm_t *hWave);

const int listInputGpio[8] = {11, 10, 14, 6, 13, 12, 5, 4};
static char remoteHost[8][4] = {"Pi1", "Pi2", "Pi3", "Pi4", "Pi5", "Pi6", "Pi7", "Pi8"};
// static char remoteHost[8][4] = {"Pi2", "Pi2", "Pi3", "Pi2", "Pi2", "Pi2", "Pi2", "Pi2"};

inline int min(int a, int b) {
	return (a>b)? b:a;
}

class Phone {
    public:
        struct sockaddr_in udp_cli_addr;
		int input_pin;

        Phone(char *ip, int pin){
			pinMode (pin, INPUT);
			pullUpDnControl (pin, PUD_UP );
			input_pin = pin;

			struct hostent *he;
			if ( (he = gethostbyname(ip) ) == NULL ) {
				printf("Cannot get host by name %s\n", ip);
				exit(1); /* error */
			}

			memcpy(&udp_cli_addr.sin_addr, he->h_addr_list[0], he->h_length);
            // udp_cli_addr.sin_addr.s_addr = inet_addr(ip);
            udp_cli_addr.sin_family = AF_INET;
            udp_cli_addr.sin_port = htons(UDP_PORT);
        }
};


int main(int argc, char *argv[])
{
	snd_pcm_t *hWaveIn;
	int result;
	int datasent;
	short *data_buffer;
	double volume = 1;
	int connection = -1;
    std::vector<Phone> phones;
	const char* audioTarget = "default";
	int audioSamplePerSec = 48000;
	int audioChannels = 1;
	int audioBytesPerSample = 2;
	int audioNumBuffer = 4;
	int bufferChunk = 128;
	int bufferSize;
	bool test = false;
	int indexSelfMic;

    wiringPiSetup ();
	char hostname[4];
	gethostname(hostname, 4);

    for (int i=0; i < 8; i++){
		if (strcmp(hostname, remoteHost[i]) != 0){
			Phone phone(remoteHost[i], listInputGpio[i]);
        	phones.push_back(phone);
		} else {
			indexSelfMic = listInputGpio[i];
			pinMode (indexSelfMic, INPUT);
			pullUpDnControl (indexSelfMic, PUD_UP );
		}
    }

	for(int i = 1; i < argc; i++) {
		if(!strcmp(argv[i], "--rate") && (i+1) < argc) {
			audioSamplePerSec = atoi(argv[i+1]);
			i++;
		} else if(!strcmp(argv[i], "--channel") && (i+1) < argc) {
			audioChannels = atoi(argv[i+1]);
			i++;
		} else if(!strcmp(argv[i], "--chunksize") && (i+1) < argc) {
			bufferChunk = atoi(argv[i+1]);
			i++;
		} else if(!strcmp(argv[i], "--chunknum") && (i+1) < argc) {
			audioNumBuffer = atoi(argv[i+1]);
			i++;
		} else if(!strcmp(argv[i], "--device") && (i+1) < argc) {
			audioTarget = argv[i+1];
			i++;
		} else if(!strcmp(argv[i], "--test") && (i+1) < argc) {
			test = true;
			pullUpDnControl (indexSelfMic, PUD_DOWN );
			i++;
		}
	}

	bufferSize = bufferChunk*audioChannels*audioBytesPerSample;

	setScheduler();

	if((connection = socket(AF_INET, SOCK_DGRAM, 0)) == -1) {
		logMessage("Erreur Winsock");
		return 2;
	}

	int flags;
	flags = fcntl(connection, F_GETFL, 0);
	fcntl(connection, F_SETFL, flags | O_NONBLOCK);
	flags = 1;
	setsockopt(connection, SOL_SOCKET, SO_BROADCAST, &flags, sizeof(flags));

	result = snd_pcm_open(&hWaveIn, audioTarget, SND_PCM_STREAM_CAPTURE, 0);
	if(result < 0) {
		logMessage("Failed to open waveform input device.");
		return 3;
	}

	setHwParams(hWaveIn, audioChannels, audioBytesPerSample, audioSamplePerSec, bufferChunk, audioNumBuffer);
	dumpParams(hWaveIn);

	snd_pcm_prepare(hWaveIn);
	data_buffer = (short*)calloc(bufferSize, 1);

	logMessage("Recording...");
	while(1) {

		result = snd_pcm_readi(hWaveIn, data_buffer, bufferChunk);

		if(result < 0) {
			printf("Error %d, errno: %d\n", -result, errno);
			result = snd_pcm_recover(hWaveIn, result, 0);
			logMessage("overload");
		}
		if(result < 0) {
			printf("snd_pcm_... failed\n");
			continue;
		}
		short max = 0;
		if(volume != 1.0f) {
			for(int i = 0; i < bufferSize/2; i++) {
				data_buffer[i] = volume * data_buffer[i];
				if(max < data_buffer[i])
					max = data_buffer[i];
			}
		}
		if(max > 20000)
			printf("max = %d\n", max);
		if(result > 0 && result < bufferChunk) printf("Short write : %d\n", result);
		if(result == bufferChunk) {
			if (digitalRead(indexSelfMic) == LOW){
				for (std::vector<int>::size_type i=0; i < phones.size(); i++) {
					if ((digitalRead(phones[i].input_pin) == LOW) || (test)){
						for(datasent = 0 ; datasent < bufferSize;) {
							result = sendto(connection, ((char*)data_buffer) + datasent, min(bufferSize - datasent, PACKETSIZE), MSG_NOSIGNAL, (struct sockaddr*)&(phones[i].udp_cli_addr), sizeof(sockaddr_in));
							if(result == -1 && errno == EWOULDBLOCK)
								result = 0;

							if(result == -1) {
								printf("Socket error, errno: %d\n", errno);
								break;
							}
							datasent += result;
						}
					}
				}
			}
		}
	}

	close(connection);
	return 0;
}

void setScheduler()
{
	struct sched_param sched_param;

	if (sched_getparam(0, &sched_param) < 0) {
		printf("Scheduler getparam failed...\n");
		return;
	}
	sched_param.sched_priority = sched_get_priority_max(SCHED_FIFO);
	if (!sched_setscheduler(0, SCHED_FIFO, &sched_param)) {
		printf("Scheduler set to Round Robin with priority %i...\n", sched_param.sched_priority);
		fflush(stdout);
		return;
	}
	printf("!!!Scheduler set to Round Robin with priority %i FAILED!!!\n", sched_param.sched_priority);
}


void setHwParams(snd_pcm_t *hWave, int numChannels, int bytesPerSample, int samplePerSec, int period, int numBuffer) {
	snd_pcm_hw_params_t *hwparams;
	int result;

	snd_pcm_hw_params_alloca(&hwparams);

	result = snd_pcm_hw_params_any(hWave, hwparams);
	if(result < 0) {
		printf("snd_pcm_hw_params_any failed: %s\n", snd_strerror(result));
		return;
	}

	result = snd_pcm_hw_params_set_format(hWave, hwparams, SND_PCM_FORMAT_S16_LE);
	if(result < 0) {
		printf("snd_pcm_hw_params_set_format failed: %s\n", snd_strerror(result));
		return;
	}

	result = snd_pcm_hw_params_set_rate(hWave, hwparams, samplePerSec, 0);
	if(result < 0) {
		printf("snd_pcm_hw_params_set_rate failed: %s\n", snd_strerror(result));
		return;
	}

	result = snd_pcm_hw_params_set_channels(hWave, hwparams, numChannels);
	if(result < 0) {
		printf("snd_pcm_hw_params_set_channels failed: %s\n", snd_strerror(result));
		return;
	}

	result = snd_pcm_hw_params_set_access(hWave, hwparams, SND_PCM_ACCESS_RW_INTERLEAVED );
	if(result < 0) {
		printf("snd_pcm_hw_params_set_access failed: %s\n", snd_strerror(result));
		return;
	}

	snd_pcm_uframes_t period_size = period;
	int dir = 0;
	result = snd_pcm_hw_params_set_period_size_near(hWave, hwparams, &period_size, &dir);
	if(result < 0) {
		printf("snd_pcm_hw_params_set_period_size_near failed: %s\n", snd_strerror(result));
		return;
	}

	snd_pcm_uframes_t target_buffer_size = period_size*numBuffer;
	result = snd_pcm_hw_params_set_buffer_size_near(hWave, hwparams, &target_buffer_size);
	if(result < 0) {
		printf("snd_pcm_hw_params_set_buffer_size_near failed: %s\n", snd_strerror(result));
		return;
	}

	result = snd_pcm_hw_params(hWave, hwparams);
	if(result < 0) {
		printf("snd_pcm_hw_params failed: %s\n", snd_strerror(result));
		return;
	}
}

void dumpParams(snd_pcm_t *hWave) {
	snd_output_t *out;

	snd_output_stdio_attach(&out, stderr, 0);
	snd_output_printf(out, "dump :\n");
	snd_pcm_dump_setup(hWave, out);
	snd_output_close(out);
}