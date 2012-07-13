#****************************************************************************#
# mutation-call-by-coverage
#$Id: Makefile 1778 2012-07-11 16:41:02Z favorov $
#****************************************************************************#
name=downSAM

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

