# This is the PyAudio distribution makefile.

.PHONY: docs clean

EPYDOC ?= epydoc

VERSION := 0.2.6
DOCS_OUTPUT=docs/
DOC_NAME := PyAudio-$(VERSION)
DOC_URL=http://people.csail.mit.edu/hubert/pyaudio/

what:
	@echo "make targets:"
	@echo
	@echo " tarball    : build source tarball"
	@echo " docs       : generate documentation (requires epydoc)"
	@echo " clean      : remove build files"
	@echo
	@echo "To build pyaudio, run:"
	@echo
	@echo "   python setup.py install"

clean:
	@rm -rf build dist MANIFEST $(DOCS_OUTPUT) src/*.pyc

######################################################################
# Documentation
######################################################################

docs:
	@cd src; \
	$(EPYDOC) -v -o ../$(DOCS_OUTPUT) --name $(DOC_NAME) --url $(DOC_URL) \
	--no-private pyaudio.py

######################################################################
# Source Tarball
######################################################################
tarball: docs $(SRCFILES) MANIFEST.in
	@python setup.py sdist
