#!/bin/python3 
#requires python3
#$Id$
import os
import re
import sys
import configparser

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
slides:.""";
	print(sample_config)
	return;


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

print(slides)

if "downsampling" not in config.sections():
	print("no downsampling section section in "+sys.argv[1]+" .")
	sys.exit(1)

downsamples=config.options("downsampling")

print(downsamples)


for sec in config.sections():
	print ("[{}]".format(sec))
	for opt in config.options(sec):
		if (config.get(sec,opt)==None):
			print ("{}".format(opt))
		else:
			print ("{}:{}".format(opt,config.get(sec,opt)))
