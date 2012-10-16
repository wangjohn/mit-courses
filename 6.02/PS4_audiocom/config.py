class Options:
    def __init__(self):
        # Source and Sink options
        self.srctype = 'random' # options are '0' (null), '1' (all 1's), '01' (for unitstep), 'random'
        self.numbits = 200 # number of data bits (for the file=None option)
        self.fname = None # if set, data is read from the file; should be a string giving filename
        self.header = True # True <==> use a 16-bit header specifying the length

        # Phy-layer Transmitter and Receiver options
        self.samplerate = 48000
        self.chunksize = 256
        self.prefill = 60
        self.spb = 256          # samples per bit
        self.channel = [1000] # channel type: bypass (synthetic) or carrier freq
        self.changap = 500    # gap between channel center freqs (Hz)
        self.silence = 80
        self.carrier_preamble = False # don't change this!

        # Modulation (signaling) and Demodulation options        
        self.ktype = 'on_off' # keying (signaling): {'on_off', 'bipolar'}
        self.demod = 'envelope'
        self.one = 1.0          # voltage for bit "1"

        # BypassChannel options
        self.bypass = False
        self.noise = 0.25 # Gaussian noise variance for bypass channel
        self.lag = 0      # channel lag (delay) for bypass channel
        self.h = "1" # unit sample response for bypass channel; given as string with elements seperated by a space each

        # Got graphs?
        self.graph = False  # True <==> plot some interesting graphs
