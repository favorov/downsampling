#$Id: $

import glob
import os.path
import sys
import re

samtools_folder="../../tools-src/samtools/samtools-0.1.18/"
bamfiles=glob.glob('*bam')
for bam in bamfiles:
	name=bam[:-4]
	issam=os.path.isfile(name+".sam")
	print bam, issam
	if os.system(samtools_folder+"samtools view -h "+bam+" > "+name+".uncured.sam") != 0 :
		print "Cannot convert "+bam+" to sam."
		sys.exit()
	sam_in = open(name+".uncured.sam")
	sam_out= open(name+".sam","w")
	for line in sam_in:
		if line[0:3]=="@RG":
			if re.search(r"ID:\w+",line): 
				sam_out.write(line)
			else:
				sam_out.write("@RG\tID:"+name+"\t"+line[4:])
		else:
			sam_out.write(line)
	sam_in.close()
	sam_out.close()
	os.unlink(name+".uncured.sam")
	if os.system(samtools_folder+"samtools view -Sbh "+name+".sam"+" > "+name+".unsorted.bam") != 0 :
		print "Cannot convert "+name+"sam"+" to bam."
		sys.exit()
	if not issam:
		os.unlink(name+".sam")
	if os.system(samtools_folder+"samtools sort "+name+".unsorted.bam "+name) != 0 :
		print "Cannot sort "+bam+"."
		sys.exit()
	os.unlink(name+".unsorted.bam")
	if os.system(samtools_folder+"samtools index "+bam) != 0 :
		print "Cannot index "+bam+"."
		sys.exit()
