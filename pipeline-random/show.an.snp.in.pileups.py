#$Id: show.an.snp.in.vcfs.py 1851 2012-12-13 06:22:56Z favorov $

import glob
import sys
import re
import subprocess

snp_mask=11642
fileglob='piplleuppe.*' 

files=glob.glob(fileglob)


for thefile in files:
	if re.search("\.gz$",thefile):
		stream=subprocess.Popen(["gzip -cd "+thefile],shell=True,stdout=subprocess.PIPE).stdout
	else:
		stream=open(thefile)	
	for line in stream:
	#test whether one of the fields match snp_mask 
		if (re.search(r"\t%s\t" % snp_mask,line)):
			print thefile,":\n",line
	stream.close()
