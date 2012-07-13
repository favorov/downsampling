#****************************************************************************#
# mutation-call-by-coverage
#$Id$
#****************************************************************************#

.PHONY:	all zip tar.gz clean fullclean

all:
	cd cheapseq; $(MAKE) all
	cd noiser; $(MAKE) all
	cd downSAM; $(MAKE) all

clean:
	cd cheapseq; $(MAKE) clean
	cd noiser; $(MAKE) clean
	cd downSAM; $(MAKE) clean

fullclean:
	cd cheapseq; $(MAKE) fullclean
	cd noiser; $(MAKE) fullclean
	cd downSAM; $(MAKE) fullclean
	rm -f coverage.tar.gz

zip: tar.gz

tar.gz: fullclean coverage.tar.gz

coverage.tar.gz:
	tar -cvf- cheapseq noiser downSAM --exclude .svn --exclude chr9.fa.gz --exclude reads* --exclude mutations* ccvars boostdirs Makefile | gzip -c > coverage.tar.gz

~/include/ccvars: ../ccvars
	@if [ ! -d ~/include ]; then mkdir ~/include && echo "Creating ~/include...";fi
	@cp ../ccvars $(HOME)/include && echo "Copying ccvars..."

