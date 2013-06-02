#!/bin/python3 
#requires python3
#$Id$
import os
import re
import sys
import configparser
import subprocess

def write_sample_config():
	sample_config="""
[slides]
#list of slides, they will be merged on run
slide_1_normal.bam
slide_2_normal.bam
slide_3_normal.bam
[downsampling]
#dowsampling schedule each line is level(1 out for level in):runs
10:5
100:50
[flow]
cores:16
[program_folders]
#program prefix (path); their defaults are ""
downSAM:
samtools:
bcftools:
[folders]
#defaults is scripts
scripts:scripts
#default is "downsamples"
downsamples:downsamples
#default is "bcfs"
bcfs:bcfs
#default is .
slides:."""
	print(sample_config)
	return

def fulltoolname(toolname,toolpath=None):
	if toolpath==None or toolpath=="":
	# we will try to find it with which; virtually if it works - it works, no checks needed!
	#but the thing is new, so we will check it
		try:
			resultfulltoolname=os.popen("which "+toolname).read().rstrip()
			if not resultfulltoolname:
				throw
		except:
			print("Which did not find "+resulttoolname+" and its folder is not correctly given in config. So what?")
			sys.exit(1)
	else: #folder is given, we are to add it and to test it
		resultfulltoolname=os.path.join(toolpath,toolname)
	if not os.path.isfile(resultfulltoolname): #here, we test that file exist
		print("The file "+resultfulltoolname+" does not exist... trying which...")
		return fulltoolname(toolname) #trying which	
	if subprocess.call("[ -x "+resultfulltoolname+" ]",shell=True): 
	#we test that it is exec, the thing return 0 if it is OK
	#if test returned 1, it file is not exec
		print("The file "+resultfulltoolname+" is not executable. ... trying which...")
		return fulltoolname(toolname) #trying which	
	return resultfulltoolname

#def sam2bam_command(,name):
#	command_line=samtools_dir
#	return command_line

#here, we start the part that works only in __main__

def my_info():
	info_message="""pipeline-real A. Favorov (c) 2013. 
Part of the coverage project. To know more, ask --help"""
	print(info_message)
	return

def my_help():
	help_message="""pipeline-real is a part of the coverage project
The only parameter is one of following: 
the configuration file name
--help
--write-sample-config"""
	print(help_message)
	return

def main():
	#vars that define the behavoiur of the things
	if_bam=[]
	#boolean, bam or sam for each slide
	#all downsamples are bams, whatever
	slide_names=[]
	#names of slides without extension
	downsamples={}
	#dictionary scale:repeats; both are integers

	if len(sys.argv)<2:
		my_info()
		sys.exit(0)

	if len(sys.argv)>2:
		print ("\nToo many paraneters!\n")
		sys.exit(1)

	if sys.argv[1] in ["--help","--h","-h","-?","-help"]:
		my_help()
		sys.exit(0)
				
	if sys.argv[1]=="--write-sample-config":
		write_sample_config()
		sys.exit(0)

	if not os.path.exists(sys.argv[1]):
		print ("Cannot open config "+sys.argv[1]+".")
		sys.exit(1)

	config = configparser.ConfigParser(allow_no_value=True)
	config.read(sys.argv[1])

	#here, we start to check slides

	if "slides" not in config.sections():
		print("no slides section in "+sys.argv[1]+" .")
		sys.exit(1)

	slides=config.options("slides")

	for slide in slides:
		if not os.path.exists(slide):
			print("Cannot open slide: "+slide+" .")
			sys.exit(1)
		#file exist
		if re.search(r"\.bam$",slide):
			if_bam.append(True)
		elif re.search(r"\.sam$",slide):
			if_bam.append(False)
		else:
			print("Unknown slide extension"+slide+"\n")
			sys.exit(1)
		#slide name ok
		slide_names.append(slide[:-4])
		
	#we checked slides and we know bams and sams

	if "downsampling" not in config.sections():
		print("no downsampling section section in "+sys.argv[1]+" .")
		sys.exit(1)

	for scale in config.options("downsampling"):
		try:
			scale_int=int(scale)
			scale_int + 1 #test for int, do nothing if OK
		except TypeError:
			print("Downsampling scale "+scale+" is not an integer.\n")
			sys.exit(1)
		repeats=config["downsampling"][scale]
		try:
			repeats=int(repeats)
			repeats + 1 #test for int, do nothing if OK
		except TypeError:
			print("Downsampling repeats at scale "+scale+" is "+repeats+" and it is not an integer.\n")
			sys.exit(1)
		downsamples[scale_int]=repeats
				

	if "program_folders" not in config.sections():
		print("no program_folders section section in "+sys.argv[1]+" . Is it OK?")

	samtools=fulltoolname('samtools',config["program_folders"].get("samtools"))
	downSAM=fulltoolname('downSAM',config["program_folders"].get("downSAM"))
	bcftools=fulltoolname('bcftools',config["program_folders"].get("bcftools"))

	print(downsamples)

	print(downSAM)
	print(samtools)
	print(bcftools)

	print(slide_names)

	sys.exit(0)

	for sec in config.sections():
		print ("[{}]".format(sec))
		for opt in config.options(sec):
			if (config.get(sec,opt)==None):
				print ("{}".format(opt))
			else:
				print ("{}:{}".format(opt,config.get(sec,opt)))

#here, we finally run it all :)
if __name__ == "__main__":
    main()

