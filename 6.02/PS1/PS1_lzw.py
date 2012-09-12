# template file for 6.02 PS1, Python Task 4 (LZW Compression/Decompression)
import sys
from optparse import OptionParser
import struct
import array

def compress(filename):
    """
    Compresses a file using the LZW algorithm and saves output in another file.
    Arguments: 
        filename: filename of file to compress.
    Returns:
        None.
    """
    pass

def uncompress(filename):
    """
    Decompresses a file using the LZW algorithm and saves output in another file.
    Arguments: 
        filename: filename of file to decompress.
    Returns:
        None.
    """

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--filename", type="string", dest="fname", 
                      default="test", help="file to compress or uncompress")
    parser.add_option("-c", "--compress", action="store_true", dest="uncomp", 
                      default=True, help="compress file")
    parser.add_option("-u", "--uncompress", action="store_true", dest="uncomp", 
                      default=False, help="uncompress file")

    (opt, args) = parser.parse_args()
    
    if opt.uncomp == True:
        uncompress(opt.fname)
    else:
        compress(opt.fname)
