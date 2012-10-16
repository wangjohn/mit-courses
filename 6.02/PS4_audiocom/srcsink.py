# audiocom library: Source and sink functions
from sendrecv import *
from graphs import *
import binascii

def bin_to_int(binary_list):
    out = 0
    for ix in xrange(len(binary_list)):
        out += binary_list[ix] * (2**(len(binary_list) - 1 - ix))
    return out

class Frame:
    def __init__(self, data, header, trailer=None):
        # Frame contains 2-byte header length followed by the payload (data)
        self.bits = data
        if header:
            h = list(bin(len(data))[2:])
            h = [int(x) for x in h]
            self.header = [0]*(16 - len(h)) + h # get it up to 16 bits
            self.bits = self.header + data
        if trailer is not None:
            self.trailer = bin(abs(binascii.crc32(''.join(chr(item) for item in self.bits))))[2:] 
            self.bits = numpy.append(self.bits, numpy.array(list(self.trailer), dtype=int))

class Source:
    def __init__(self, srctype, hdr, numbits, filename=None):
        '''
        Create a source of the given srctype, with an optional hdr (if
        hdr is True), with numbits payload bits, from an image file if
        specified or according to the srctype.
        self.srctype = {zeroes, carrier, unitstep, random, or imgfile}.
        Return the list of bits (optional header + payload)
        '''
        self.srctype = srctype
        self.hdr = hdr          # to use a header or not?
        if srctype == "0":             # no data, no carrier
            self.srctype = "zeroes"
            self.payload = [0]*numbits
        elif srctype == "1":           # only carrier
            self.srctype = "carrier"
            self.payload = [1]*numbits
        elif srctype == "01":
            self.srctype = "unitstep"
            self.payload = [0]*(int(numbits/2)) + [1]*(int(numbits/2)) + ([1] if numbits%2 == 1 else [])
        else:
            if filename is not None:
                self.fname = filename
                if filename.endswith('.png') or filename.endswith('.PNG'):
                    import image
                    self.srctype = "png"
                    self.payload = image.bits_from_image(filename)
                else:           # assume it's text
                    self.srctype = "text"
                    self.payload = self.text2bits(filename)
            else:               # srctype is "random" by default
                self.srctype = "random"
                self.payload = [random.randint(0,1) for i in range(numbits)]
        self.frame = Frame(self.payload, header=hdr)

    def text2bits(self, filename):
        f = open(filename, 'r')
        bits = []
        line = f.read()
        for c in line:
            bits.extend(self.int2bits(ord(c), 8))
        return bits

    def int2bits(self, x, width): 
        return tuple((0,1)[x>>j & 1] for j in xrange(width-1,-1,-1)) 

class Sink:
    def __init__(self, receiver, hdr, srctype):
        self.rcvr = receiver
        self.hdr = hdr
        self.srctype = srctype
        if hdr:
            self.hlen = len(Frame([], header=True).header) 

    def process(self, recd_bits, softinfo, fname=None):
        blen = self.rcvr.preamble.barkerlen()
        print 'Recd preamble as', recd_bits[:blen]
        if self.hdr:
            header = recd_bits[blen:blen+self.hlen]
            length = bin_to_int(header)
            print 'Length from header', length
            startdata = blen + 16  # data begins at bit offset 27 (= 11 + 16)
        else:
            length = len(recd_bits) - blen
            startdata = blen

        rcd_preamble = recd_bits[:blen]
        rcd_data = recd_bits[startdata:startdata+length]
        print 'Recd', len(rcd_data), 'data bits:'
        if self.srctype == "png": 
            image.image_from_bits(rcd_data, 'rcd-'+fname)
        elif self.srctype == "text":
            print 'Text recd:', self.bits2text(rcd_data)

        return numpy.array(rcd_data, dtype=int)

    def bits2text(self, bits):
        text = []
        intbits = numpy.array([], dtype=numpy.uint8)
        for i in xrange(len(bits)/8):
            intbits = numpy.append(intbits, self.bits2int(bits[i*8:(i+1)*8]))
        for c in intbits:
            text.append(chr(c))
        return  "".join([t for t in text])

    def bits2int(self, bits):
        out = 0
        for ix in xrange(len(bits)):
            out += bits[ix] * (2**(len(bits) - 1 - ix))
        return int(out)
