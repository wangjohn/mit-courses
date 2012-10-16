import Image

def bin_nbit(number, n):
    out = bin(number)[2:]
    if len(out) > n:
        raise Exception, "number too big to be stored in %d bits: %d" % (n, number)
    while len(out) < n:
        out = '0' + out
    return out

def bits_from_image(filename):
    im = Image.open(filename)
    im = im.convert('L')
    d = list(im.getdata())
    return [int(i) for i in "".join(bin_nbit(j, 8) for j in d)]

def bits_from_colored_image(filename):
    i = Image.open(filename)
    i = i.convert('RGB')
    d = list(i.getdata())
    return [int(k) for k in "".join("".join(bin_nbit(i, 8) for i in j) for j in d)]

def image_from_bits(bits,filename):
    i = Image.new('L',(32,32))
    d = []
    for ix in xrange(32*32):
        b = bits[ix*8 : (ix+1)*8]
        while len(b) < 8:
            b.append(0) # pad with zeros if we got too few bits
        d.append(bin_to_int(b))
    i.putdata(d)
    i.save(filename)
    return d

def colored_image_from_bits(bits, filename):
    i = Image.new('RGB', (32,32))
    d = []
    tmp = []
    for ix in xrange(32*32*3):
        b = bits[ix*8 : (ix+1)*8]
        while len(b) < 8:
            b.append(0)
        tmp.append(bin_to_int(b))
        if len(tmp) == 3:
            d.append(tuple(tmp))
            tmp = []
    i.putdata(d)
    i.save(filename)
    return d

def bin_to_int(binary_list):
    out = 0
    for ix in xrange(len(binary_list)):
        out += binary_list[ix] * (2**(len(binary_list) - 1 - ix))
    return out

