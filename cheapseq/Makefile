#****************************************************************************#
# mutation-call-by-coverage
#$Id: create_mutation_list.mak 1749 2012-06-21 08:02:39Z favorov $
#****************************************************************************#


.PHONY:	all objs clean 

all:
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) -f create_mutation_list.mak 

clean:
	$(MAKE) -f create_mutation_list.mak clean

objs:
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) objs -f create_mutation_list.mak

