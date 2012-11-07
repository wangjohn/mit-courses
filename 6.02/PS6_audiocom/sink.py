from common import hamming

def source(data, numbits, spb, fname):
    if data == "0":             # no data, no carrier
        bits = [0]*numbits
        datatype = 'zeroes'
    elif data == "1":           # only carrier
        bits = [1]*numbits
        datatype = 'carrier'
    elif data == "01":
        # unit-step response pattern
        bits = [0]*(2048/spb) + [1]*(2048/spb)
        datatype = 'unitstep'
    else:
        if fname is not None:
            bits = image.bits_from_image(fname)
            datatype = 'file'
        else:
            bits = [random.randint(0,1) for i in range(numbits)]
            datatype = 'random'

    return bits, datatype

def sink(samples, datatype, spb, demodtype):
    het_samples, demod_samples = receiver.demodulate(samples)
    print 'demod', len(demod_samples)            
    receiver.get_snr(demod_samples[:11*spb]) # snr over known Barker sequence
    recd_bits = receiver.mapper.demap2bits(demod_samples, demodtype)
    print recd_bits

    if opt.header:
        # Barker seq is 11 bits; the 16 bits following are the
        # header (length field)
        header = recd_bits[11:27]
        length = bin_to_int(header)
        print 'Length from hdr', length
        startdata = 27  # data begins at bit offset 27 (= 11 + 16)
    else:
        length = len(recd_bits) - 11
        startdata = 11

    rcd_preamble = recd_bits[:11]
    rcd_data = recd_bits[startdata:startdata+length]
    print 'Sent %d data bits. Recd %d data bits' % (len(bits), length)
#            print 'R_dat:', rcd_data
    if datatype == "file":
        image.image_from_bits(rcd_data,'rcd-'+opt.fname)
    hd, err = hamming(bits, rcd_data)
    print 'Hamming distance for payload:', hd, 'BER:', err

    if datatype == "unitstep":
        het_samples, demod_samples = receiver.demodulate(samples)
        stepoffset = 11*opt.spb + 2040 # 2048 is the number of 0's
        usr = step2sample(demod_samples[stepoffset:])
        plot_samples(demod_samples[stepoffset:min(stepoffset+400,len(samples_rx))], 'unit-step response')

    if opt.graph:
        plot_graphs()

