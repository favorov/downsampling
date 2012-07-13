#****************************************************************************#
# mutation-call-by-coverage
#$Id$
#****************************************************************************#

name=noiser

.PHONY:	all objs clean fullclean

all: ~/include/ccvars
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) -f $(name).mak 

clean:
	$(MAKE) -f $(name).mak clean

fullclean:
	$(MAKE) -f $(name).mak fullclean
	
objs:
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) objs -f $(name).mak

~/include/ccvars: ../ccvars
	@if [ ! -d ~/include ]; then mkdir ~/include && echo "Creating ~/include...";fi
	@cp ../ccvars $(HOME)/include && echo "Copying ccvars..."

