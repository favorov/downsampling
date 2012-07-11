#****************************************************************************#
# mutation-call-by-coverage
#$Id: create_mutation_list.mak 1749 2012-06-21 08:02:39Z favorov $
#****************************************************************************#


.PHONY:	all objs clean fullclean

all: ~/include/ccvars
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) -f noiser.mak 

clean:
	$(MAKE) -f noiser.mak clean

fullclean:
	$(MAKE) -f noiser.mak fullclean
	
objs:
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) objs -f noiser.mak

~/include/ccvars: ../ccvars
	@if [ ! -d ~/include ]; then mkdir ~/include && echo "Creating ~/include...";fi
	@cp ../ccvars $(HOME)/include && echo "Copying ccvars..."

