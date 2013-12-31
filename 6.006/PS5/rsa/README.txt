RSA On the Knight's Shield (KT) Chip code for MIT 6.006 Fall 2011 PS5

The code distribution contains the following files:
  * rsa.py - main body for the RSA code
  * rsa_test.py - tester used for grading
  * big_num.py - large number arithmetic
  * big_num_test.py - tests showcasing the API in big_num.py
  * ks_primitives.py - software emulation for the the KT chip builtins
  * ks_primitives_test.py - tests showcasing the API in ks_primitives.py
  * image_testgen.rb - testcase generator
  * test/*.in - RSA test inputs
  * test/*.gold - outputs that we believe to be correct for the RSA test inputs
  * visualizer/bin/visualizer.html - visualizes the image decryption output
  * visualizer/README.txt - Readme for the visualizer source code
  * visualizer/* - visualizer source code


USAGE

image_testgen.rb takes two command-line arguments, the source image and the
length of the public key in bytes (digits in the KS large-number library).

Command-line example:
    ruby image_testgen.rb images/smiley.png 4 > tests/1verdict_16.in


DEPENDENCIES

{rsa,big_num,ks_primitives}.py have been tested on Python 2.7, Python 3.2, and
PyPy 1.6.

The test generator was tested in Ruby 1.9.2, and requires OpenSSL support, as
well as the rmagick gem. The following commands will install the dependencies on
Ubuntu 11.10 and above.
  sudo apt-get install ruby1.9.1-full build-essential
  sudo update-alternatives --set ruby /usr/bin/ruby1.9.1
  sudo apt-get install libmagickcore-dev libmagickwand-dev
  sudo env REALLY_UPDATE_GEM_SYSTEM=1 gem update --system
  sudo gem update --system
  sudo gem install rmagick

The lines below will install the dependencies on Ubuntu 11.04 and below.
  sudo apt-get install ruby rubygems ruby1.8-full build-essential
  sudo apt-get install libmagickcore-dev libmagickwand-dev
  sudo gem install rmagick
