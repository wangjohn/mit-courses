"""
PyAudio Example: Make a wire between input and output (i.e., record a
few samples and play them back immediately).

This is the half duplex version.
"""

import pyaudio
import sys

CHUNK = 1024
WIDTH = 2
CHANNELS = 2
RATE = 44100
RECORD_SECONDS = 5

if sys.platform == 'darwin':
    CHANNELS = 1

p = pyaudio.PyAudio()

# Open input stream using default device:
stream_input = p.open(format=p.get_format_from_width(WIDTH),
                      channels=CHANNELS,
                      rate=RATE,
                      input=True,
                      frames_per_buffer=CHUNK)

# Open out stream using default device:
stream_output = p.open(format=p.get_format_from_width(WIDTH),
                       channels=CHANNELS,
                       rate=RATE,
                       output=True,
                       frames_per_buffer=CHUNK)

print("* recording")

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream_input.read(CHUNK)
    stream_output.write(data, CHUNK)

print("* done")

stream_input.stop_stream()
stream_output.stop_stream()
stream_input.close()
stream_output.close()
p.terminate()
