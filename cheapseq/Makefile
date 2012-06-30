#****************************************************************************#
# mutation-call-by-coverage
#$Id: create_mutation_list.mak 1749 2012-06-21 08:02:39Z favorov $
#****************************************************************************#


.PHONY:	all objs clean 

all: ~/include/ccvars
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) -f cheapseq.mak 

clean:
	$(MAKE) -f chepseq.mak clean

objs:
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) objs -f cheapseq.mak

~/include/ccvars: ../ccvars
	@if [ ! -d ~/include ]; then mkdir ~/include && echo "Creating ~/include...";fi
	@cp ../ccvars $(HOME)/include && echo "Copying ccvars..."

