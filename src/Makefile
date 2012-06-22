#****************************************************************************#
#SeSiMCMC. Looking - for - motifs by MCMC project. (c) A. Favorov 2001
#$Id: Makefile 1332 2010-11-20 02:13:48Z favorov $
#****************************************************************************#
#this file can be started only from parent directory


.PHONY:	all objs clean 

all:
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) -f create_mutation_list.mak 

clean:
	$(MAKE) -f create_mutation_list.mak clean

objs:
	@if [ ! -d ./obj ]; then mkdir ./obj && echo "Creating ./obj...";fi
	$(MAKE) objs -f create_mutation_list.mak

