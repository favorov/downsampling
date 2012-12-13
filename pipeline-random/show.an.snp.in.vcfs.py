#$Id$

import glob
import sys
import re
import subprocess

snp_mask=11642

vcffiles=glob.glob('*.vcf.gz')

for vcffile in vcffiles:
	stream=subprocess.Popen(["gzip -cd "+vcffile],shell=True,stdout=subprocess.PIPE).stdout
	for line in stream:
		if (re.search(r"\t%s\t" % snp_mask,line)):
			print vcffile,":\n",line
	stream.close()

