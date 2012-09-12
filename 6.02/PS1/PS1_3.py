# file for PS1, Python Task 3
import matplotlib.pyplot as p
import numpy,os
import PS1_tests
from PS1_1 import huffman
from PS1_2 import decode

if __name__ == '__main__':
    # read in the image, convert into vector of pixels
    img = p.imread('PS1_fax_image.png')
    nrows,ncols,pixels = PS1_tests.img2pixels(img)

    # convert the image into a sequence of alternating
    # white and black runs, with a maximum run length
    # of 255 (longer runs are converted into multiple
    # runs of 255 followed by a run of 0 of the other
    # color).  So each element of the list is a number
    # between 0 and 255.
    runs = PS1_tests.pixels2runs(pixels,maxrun=255)

    # now print out number of bits for pixel-by-pixel
    # encoding and fixed-length encoding for runs
    print "Baseline 0:"
    print "  bits to encode pixels:",pixels.size

    print "\nBaseline 1:"
    print "  total number of runs:",runs.size
    print "  bits to encode runs with fixed-length code:",\
          8*runs.size

    print "\nBaseline 2:"
    print "  bits in Lempel-Ziv compressed PNG file:",\
          os.stat('PS1_fax_image.png').st_size*8

    # Start by computing the probability of each run length
    # by simply counting how many of each run length we have
    plist = PS1_tests.histogram(runs)

    # Experiment 1: Huffman-encoding run lengths
    cdict = huffman(plist)
    encoded_runs = numpy.concatenate([cdict[r] for r in runs])
    print "\nExperiment 1:"
    print "  bits when Huffman-encoding runs:",\
          len(encoded_runs)
    print "  Top 10 run lengths [probability]:"
    for i in xrange(10):
        print "    %d [%3.2f]" % (plist[i][1],plist[i][0])

    # Experiment 2: Huffman-encoding white runs, black runs
    plist_white = PS1_tests.histogram(runs[0::2])
    cwhite = huffman(plist_white)
    plist_black = PS1_tests.histogram(runs[1::2])
    cblack = huffman(plist_black)
    encoded_runs = numpy.concatenate(
        [cwhite[runs[i]] if (i & 1) == 0 else cblack[runs[i]]
         for i in xrange(len(runs))])
    print "\nExperiment 2:"
    print "  bits when Huffman-encoding runs by color:",\
          len(encoded_runs)
    print "  Top 10 white run lengths [probability]:"
    for i in xrange(10):
        print "    %d [%3.2f]" % (plist_white[i][1],
                                  plist_white[i][0])
    print "  Top 10 black run lengths [probability]:"
    for i in xrange(10):
        print "    %d [%3.2f]" % (plist_black[i][1],
                                  plist_black[i][0])

    # Experiment 3: Huffman-encoding run pairs
    # where each pair is (white run,black run)
    pairs = [(runs[i],runs[i+1]) for i in xrange(0,len(runs),2)]
    plist_pairs = PS1_tests.histogram(pairs)
    cpair = huffman(plist_pairs)
    encoded_pairs = numpy.concatenate([cpair[pair]
                                       for pair in pairs])
    print "\nExperiment 3:"
    print "  bits when Huffman-encoding run pairs:",\
          len(encoded_pairs)
    print "  Top 10 run-length pairs [probability]:"
    for i in xrange(10):
        print "    %s [%3.2f]" % (str(plist_pairs[i][1]),
                                  plist_pairs[i][0])

    # Experiment 4: Huffman-encoding 4x4 image blocks
    blocks = PS1_tests.pixels2blocks(pixels,nrows,ncols,4,4)
    plist_blocks = PS1_tests.histogram(blocks)
    cblock = huffman(plist_blocks)
    encoded_blocks = numpy.concatenate([cblock[b] for b in blocks])
    print "\nExperiment 4:"
    print "  bits when Huffman-encoding 4x4 image blocks:",\
          len(encoded_blocks)
    print "  Top 10 4x4 blocks [probability]:"
    for i in xrange(10):
        print "    0x%04x [%3.2f]" % (plist_blocks[i][1],
                                      plist_blocks[i][0])

    """
    # make sure we didn't goof somehow => display decoded image
    decoded_blocks = decode(tree_block,encoded_blocks)
    decoded_pixels = PS1_tests.blocks2pixels(decoded_blocks,
                                         nrows,ncols,4,4)
    decoded_img = PS1_tests.pixels2img(decoded_pixels,nrows,ncols)
    p.figure()
    p.title('Image decoded from 4x4 encoded blocks')
    p.imshow(decoded_img)
    p.show()
    """
