#****************************************************************************#
# mutation-call-by-coverage
#$Id: create_mutation_list.mak 1749 2012-06-21 08:02:39Z favorov $
#****************************************************************************#

.PHONY:	all zip tar.gz clean fullclean

all:
	cd cheapseq; $(MAKE) all

clean:
	cd cheapseq; $(MAKE) clean

fullclean:
	cd cheapseq; $(MAKE) fullclean
	rm coverage.tar.gz

zip: tar.gz

tar.gz: fullclean coverage.tar.gz

coverage.tar.gz:
	tar -cvf- cheapseq --exclude .svn --exclude chr9.fa.gz --exclude reads* --exclude mutations* ccvars boostdirs Makefile | gzip -c > coverage.tar.gz

~/include/ccvars: ../ccvars
	@if [ ! -d ~/include ]; then mkdir ~/include && echo "Creating ~/include...";fi
	@cp ../ccvars $(HOME)/include && echo "Copying ccvars..."

