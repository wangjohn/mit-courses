import sys, time
import pyaudio
import struct
from link_defs import * # link parameters

# Channel configuration
FORMAT = pyaudio.paFloat32

# Main audio channel class - use to send and receive samples
class AudioChannel:
    def __init__( self, samplerate, spc, prefill ):
        self.id = "Audio"
        self.p = pyaudio.PyAudio()
        self.samplerate = samplerate
        self.SAMPLES_PER_CHUNK = spc
        self.WRITE_BUFFER_PREFILL = prefill

    def xmit_and_recv( self, samples_tx ):
        # open soundcard channel
        self.soundcard_inout = self.p.open(format = FORMAT,
                                           channels = CHANNELS,
                                           rate = self.samplerate,
                                           input = True,
                                           output = True,
                                           frames_per_buffer = self.SAMPLES_PER_CHUNK)

        # Create payload
        sample_count = 0
        total_sample_count = 0
        chunk_data = [ "" ]
        chunk_number = 0
        for s in samples_tx:
            chunk_data[ chunk_number ] += struct.pack( 'f', s)
            total_sample_count += 1
            sample_count += 1
            if sample_count == self.SAMPLES_PER_CHUNK:
                chunk_number += 1
                chunk_data.append("")
                sample_count = 0

        # send payload to the soundcard and collect the received samples
        samples_rx = []
        sample_chunk_rx = []
        max_recv_samples = total_sample_count + 4000
        nsamples = 0
        for chunk in chunk_data[:self.WRITE_BUFFER_PREFILL]:
            # transmit a chunk
            self.soundcard_inout.write(chunk)
        for chunk in chunk_data[self.WRITE_BUFFER_PREFILL:]:
            # transmit a chunk
            self.soundcard_inout.write(chunk)
            # receive a chunk
            rx_sample_count = 0
            sample_chunk_rx = []
            try:
                sample_chunk_rx.extend( struct.unpack( 'f' * self.SAMPLES_PER_CHUNK, self.soundcard_inout.read( self.SAMPLES_PER_CHUNK ) ) )
                nsamples += self.SAMPLES_PER_CHUNK
                samples_rx.extend(sample_chunk_rx)
            except IOError as ex:
                sys.stderr.write( "IOError %s\n" % ex )

        while nsamples < max_recv_samples:
            # receive a chunk
            rx_sample_count = 0
            sample_chunk_rx = []
            try:
                sample_chunk_rx.extend( struct.unpack( 'f' * self.SAMPLES_PER_CHUNK, self.soundcard_inout.read( self.SAMPLES_PER_CHUNK ) ) )
                nsamples += self.SAMPLES_PER_CHUNK
            except IOError:
                sys.stderr.write( "IOError\n" )
                pass
            samples_rx.extend(sample_chunk_rx)

        # close the soundcard channel    
        self.soundcard_inout.close()
        
        return samples_rx # return received samples
    
    def xmit(self, samples):
        self.soundcard_out = self.p.open(format = FORMAT,
                                         channels = CHANNELS,
                                         rate = self.samplerate,
                                         input = False,
                                         output = True,
                                         frames_per_buffer = self.SAMPLES_PER_CHUNK)
        sample_count = 0
        total_sample_count = 0
        chunk_data = [ "" ]
        chunk_number = 0
        for s in samples:
            chunk_data[ chunk_number ] += struct.pack( 'f', s)
            total_sample_count += 1
            sample_count += 1
            if sample_count == self.SAMPLES_PER_CHUNK:
                chunk_number += 1
                chunk_data.append("")
                sample_count = 0

        for chunk in chunk_data:
            # transmit a chunk
            self.soundcard_out.write(chunk)
            # receive a chunk

        self.soundcard_out.close()
        return chunk_data

    def recv(self, duration):
        self.soundcard_in = self.p.open(format = FORMAT,
                                        channels = CHANNELS,
                                        rate = self.samplerate,
                                        input = True,
                                        output = True,
                                        frames_per_buffer = self.SAMPLES_PER_CHUNK)
        nsamples = 0
        samples_rx = []
        while nsamples < duration*samplerate:
            # receive a chunk
            sample_chunk_rx = []
            try:
                sample_chunk_rx.extend( struct.unpack( 'f' * self.SAMPLES_PER_CHUNK, self.soundcard_in.read( self.SAMPLES_PER_CHUNK ) ) )
                nsamples += self.SAMPLES_PER_CHUNK
                samples_rx.extend(sample_chunk_rx)
            except IOError as ex:
                sys.stderr.write( "IOError %s\n" % ex )

        # close the soundcard channel    
        self.soundcard_in.close()
        
        return samples_rx # return received samples
