"""
PyAudio v0.2.6: Python Bindings for PortAudio.

Copyright (c) 2006-2012 Hubert Pham

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY
OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from distutils.core import setup, Extension
import sys
import os

__version__ = "0.2.6"

# Note: distutils will try to locate and link dynamically
#       against portaudio.
#
#       You probably don't want to statically link in the PortAudio
#       library unless you're building on Microsoft Windows.
#
#       In any case, if you would rather statically link in libportaudio,
#       run:
#
#       % python setup.py build --static-link
#
#       Be sure to specify the location of the libportaudio.a in
#       the `extra_link_args' variable below.

STATIC_LINKING = False

if "--static-link" in sys.argv:
    STATIC_LINKING = True
    sys.argv.remove("--static-link")

portaudio_path = os.environ.get("PORTAUDIO_PATH", "./portaudio-v19")
mac_sysroot_path = os.environ.get("SYSROOT_PATH", None)

pyaudio_module_sources = ['src/_portaudiomodule.c']

include_dirs = []
external_libraries = []
extra_compile_args = ['-fno-strict-aliasing']
extra_link_args = []
scripts = []
defines = []

if STATIC_LINKING:
    extra_link_args = [
        os.path.join(portaudio_path, 'lib/.libs/libportaudio.a')
        ]
    include_dirs = [os.path.join(portaudio_path, 'include/')]
else:
    # dynamic linking
    external_libraries = ['portaudio']
    extra_link_args = []

if sys.platform == 'darwin':
    defines += [('MACOSX', '1')]

    if mac_sysroot_path:
        extra_compile_args += ["-isysroot", mac_sysroot_path]
        extra_link_args += ["-isysroot", mac_sysroot_path]

if STATIC_LINKING:

    # platform specific configuration
    if sys.platform == 'darwin':
        extra_link_args += ['-framework', 'CoreAudio',
                            '-framework', 'AudioToolbox',
                            '-framework', 'AudioUnit',
                            '-framework', 'Carbon']

    elif sys.platform == 'cygwin':
        external_libraries += ['winmm']
        extra_link_args += ['-lwinmm']

    elif sys.platform == 'win32':
        # i.e., Win32 Python with mingw32
        # run: python setup.py build -cmingw32
        external_libraries += ['winmm']
        extra_link_args += ['-lwinmm']

    elif sys.platform == 'linux2':
        external_libraries += ['rt', 'm', 'pthread']

        # Since you're insisting on linking statically against
        # PortAudio on GNU/Linux, be sure to link in whatever sound
        # backend you used in portaudio (e.g., ALSA, JACK, etc...)

        # I'll start you off with ALSA, since that's the most common
        # today. If you need JACK support, add it here.

        external_libraries += ['asound']


pyaudio = Extension('_portaudio',
                    sources=pyaudio_module_sources,
                    include_dirs=include_dirs,
                    define_macros=defines,
                    libraries=external_libraries,
                    extra_compile_args=extra_compile_args,
                    extra_link_args=extra_link_args)

setup(name = 'PyAudio',
      version = __version__,
      author = "Hubert Pham",
      url = "http://people.csail.mit.edu/hubert/pyaudio/",
      description = 'PortAudio Python Bindings',
      long_description = __doc__.lstrip(),
      scripts = scripts,
      py_modules = ['pyaudio'],
      package_dir = {'': 'src'},
      ext_modules = [pyaudio])
