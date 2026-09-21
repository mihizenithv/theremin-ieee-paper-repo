# Theremin paper - build everything from source
#   make sim        run the ngspice simulations (~3 min)
#   make figures    regenerate the plots (needs `make sim` first)
#   make schematic  rebuild the CircuitikZ schematic (PDF + PNG)
#   make paper      compile the IEEE paper PDF
#   make all        everything, in order

PDFLATEX = pdflatex -interaction=nonstopmode -halt-on-error

.PHONY: all sim figures schematic paper clean

all: sim figures schematic paper

sim:
	cd spice && ngspice -b osc.cir      > osc.log
	cd spice && ngspice -b full.cir     > full.log
	cd spice && ngspice -b carriers.cir > carriers.log
	@grep -E "^(fa|fb)|skmax|skmin|skavg|spkmax|spkmin" spice/osc.log spice/full.log || true

figures:
	python3 analysis/make_figures.py

schematic:
	cd schematic && $(PDFLATEX) schematic.tex > /dev/null
	pdftoppm -r 300 -png -singlefile schematic/schematic.pdf schematic/schematic
	cp schematic/schematic.pdf paper/figs/schematic.pdf

paper:
	cd paper && $(PDFLATEX) theremin_paper.tex > /dev/null && $(PDFLATEX) theremin_paper.tex > /dev/null
	@echo "Built paper/theremin_paper.pdf"

clean:
	rm -f paper/*.aux paper/*.log paper/*.out schematic/*.aux schematic/*.log spice/*.log
