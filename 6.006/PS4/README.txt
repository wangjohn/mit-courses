==================
Dependencies
==================

You'll need a Python module called PIL (the Python Imaging Library),
which is used to generate the output images in this problem set.
There are a number of easy ways to get PIL.


UBUNTU 11.04 / 11.10

PIL is available as a package named python-imaging. You can install it by typing

$ sudo apt-get install python-imaging

If importing PIL in python still fails after this, you can try using pip (see 
the note on pip below):

$ sudo apt-get install python2.7-dev libfreetype6-dev libjpeg62-dev liblcms1-dev zlib1g-dev mime-support tcl8.5-dev tk8.5-dev libx11-6
$ sudo pip install PIL


MAC OS X 10.7

1. Install Xcode 4 from the Mac App Store.

If you're on an old version of OS X, you can use Xcode 3 instead. Register as an
Apple Developer (free) and download Xcode 3 for your OS from
https://developer.apple.com/downloads

2. Use pip (see the note on pip below): 

$ sudo pip install PIL


WINDOWS

You should grab one of the binaries available on the project website at

http://www.pythonware.com/products/pil/

If you are using Pythong 2.7, you should choose the binary "Python Imaging 
Library 1.1.7 for Python 2.7".


Note on pip: PIL is available from PyPI (the Python Package Index), so you can 
use pip to automatically grab, build, and install PIL. If you followed the 
software installation instructions at the beginning of the term, you should 
already have pip. If not, please do so: http://bit.ly/nmkxFd


==================
Running the tests
==================

A few simple sanity tests are provided; you can run them by typing

$ python test_dnaseq.py

To run the full comparison program, run

$ python dnaseq.py data/inputa0.fa data/inputb0.fa output.png

(You should change the first two arguments to match the inputs you're
interested in.)
