.SECONDARY:
.PHONY: all clean love 

all:

%.pdf: %.tex
	@echo pdflatex $*
	@pdflatex $*
	@pdflatex $*
	@if fgrep -e "Label(s) may have changed" $*.log > /dev/null; then \
  echo Latexing again because labels changed.; \
  echo pdflatex $*; \
  @pdflatex $*; \
fi

love:
	@echo "Not war?"

clean:
	rm -f *.aux *.ps *.pdf *.dvi *.bbl *.blg *.tmp *.log *~
