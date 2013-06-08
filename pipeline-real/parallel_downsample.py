#!/bin/python3 
#requires python3
#$Id$
import os
import re
import sys
import errno
import configparser
import shutil
import random
import subprocess
from multiprocessing import Pool

really_execute=True

def write_sample_config():
	sample_config="""
[slides]
#list of slides, they will be merged on run
slide_1_normal.bam
slide_2_normal.bam
slide_3_normal.bam
[downsampling]
#dowsampling schedule each line is level(1 out for level in):runs
10:2
100:5
[flow]
cores:16
random_seed=circumambulate
[tool_paths]
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

def run_command(command):
	print("Running: \'"+command+"\'")
	if (really_execute):
		subprocess.call(command,shell=True)
	print("Finished: \'"+command+"\'")

def fulltoolname(toolname,toolpath=None):
	if toolpath==None or toolpath=="":
	# we will try to find it with which; virtually if it works - it works, no checks needed!
	#but the thing is new, so we will check it
		try:
			resultfulltoolname=os.popen("which "+toolname).read().rstrip()
			if not resultfulltoolname:
				raise Exception("Empty which return") #exception is stupid, I do not know python system of throw/catch
		except:
			print("Which did not find "+toolname+" and its folder is not correctly given in config. So what?")
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


def make_sure_path_exists(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise # if it is not 'exist dir' - we throw exception
			#the code creates folder is it does not exist


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

def downsampled_name(name,scale,repl):
	output_file_name="{}_down_by_{}_repl_{}".format(name,scale,repl)
	return output_file_name

def main():
	#vars that define the behaviour of the things
	if_bam=[]
	#boolean, bam or sam for each slide
	#all downsamples are bams, whatever
	slide_names=[]
	#names of slides without extension
	downsamples={}
	#dictionary scale:repeats; both are integers
	#folders

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

	#folders for data, slides, etc
	if "folders" not in config.sections():
		print("No folders section section in "+sys.argv[1]+" . I will post defaults:\n \".\" for slides, \"./bcfs\" for bcfs, \"./downsamples\" for downsamples. Is it OK?")
		slides_folder="."
		bcfs_folder="./bcfs"
		downsamples_folder="./downsamples"
	else:
		if config.get("folders","slides")==None:
			print("Defult value \".\" for the slides folder")
			slides_folder="."
		else:
			slides_folder=config.get("folders","slides")

		if config.get("folders","downsamples")==None:
			print("Defult value \".downsamples\" for the downsamples folder")
			downsamples_folder="."
		else:
			downsamples_folder=config.get("folders","downsamples")
			

		if config.get("folders","bcfs")==None:
			print("Defult value \".bcfs\" for the bcfs folder")
			bcfs_folder="."
		else:
			bcfs_folder=config.get("folders","bcfs")


	make_sure_path_exists(downsamples_folder)
	make_sure_path_exists(bcfs_folder)
	#folders checked
	
	#here, we start to check slides

	if "slides" not in config.sections():
		print("no slides section in "+sys.argv[1]+" .")
		sys.exit(1)

	slides=config.options("slides")

	for slide in slides:
		if not os.path.exists(os.path.join(slides_folder,slide)):
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

	#checkin downsampling
	if "downsampling" not in config.sections():
		print("no downsampling section section in "+sys.argv[1]+" .")
		sys.exit(1)

	for scale in config.options("downsampling"):
		try:
			scale_int=int(scale)
			scale_int + 1 #test for int, do nothing if OK
		except:
			print("Downsampling scale "+scale+" is not an integer.\n")
			sys.exit(1)
		repeats=config["downsampling"][scale]
		try:
			repeats=int(repeats)
			repeats + 1 #test for int, do nothing if OK
		except:
			print("Downsampling repeats at scale "+scale+" is "+repeats+" and it is not an integer.\n")
			sys.exit(1)
		downsamples[scale_int]=repeats
				

	#cores is cores value in flow section
	if "flow" not in config.sections():
		print("No flow section section in "+sys.argv[1]+" . I suppose 2 cores and random_seed is \"circumambulate\". Is it OK?")
		cores=2
	else:
		if config.get("flow","cores") == None:
			print("No cores value in flow section section in "+sys.argv[1]+" . I suppose 2 cores. Is it OK?")
			cores=2
			random_seed="circumambulate"	
		else:
			try:
				cores_string=config.get("flow","cores")
				cores=int(cores_string)
				cores+1 + 1 #test for int, do nothing if OK
			except:
				print("Cores value "+cores_string+" is not an integer. I suppose 2 cores. Is it OK?")
				cores=2
		if config.get("flow","random_seed") == None:
			print("No random_seed value in flow section section in "+sys.argv[1]+" . I suppose it is \"circumambulate\". Is it OK?")
			random_seed="circumambulate"
		else:
			random_seed=config.get("flow","random_seed")
	#cores and random seed set
	
	#executable programs
	if "tool_paths" not in config.sections():
		print("No tool_paths section section in "+sys.argv[1]+" . Is it OK?")
		samtools=fulltoolname('samtools')
		downSAM=fulltoolname('downSAM')
		bcftools=fulltoolname('bcftools')
	else:	
		samtools=fulltoolname('samtools',config["tool_paths"].get("samtools"))
		downSAM=fulltoolname('downSAM',config["tool_paths"].get("downSAM"))
		bcftools=fulltoolname('bcftools',config["tool_paths"].get("bcftools"))
	#executable programs set

	print("slide names=",slide_names)
	print("downsamplin shedule=",downsamples)
	print("downSAM=",downSAM)
	print("samtools=",samtools)
	print("bcftools=",bcftools)
	print("cores=",cores)
	print("slides folder=",slides_folder)
	print("bcfs folder=",bcfs_folder)
	print("downsamples folder=",downsamples_folder)

	# we know everything
	#lets do something
	#if a file exist 
	#and it is not zero-length
	#we do not generate the command
	#let's make a list of commands to downsample

	pool=Pool(cores)
	#first, we convert all sams to bams
	commands=[]
	for i in range(0,len(if_bam)):
		if not if_bam[i]:
			commands.append("cd "+slides_folder+"; "+samtools+" view -Sbh "+slide_names[i]+".sam > "+slide_names[i]+".bam")
	#cd slides_folder; samtools view -Sbh slide.sam > slide.bam	
	pool.map(run_command,commands)
	pool.close()
	pool.join()
	sys.stdout.flush()
	commands[:]=[] #clean commands
	#sams to bams converted
	random.seed(random_seed)
	for slide in slide_names:
	#first, we copy slide to downsamples_folder with _down_by_1_repl_1
	#sort it and index it
		slide_1_1=os.path.join(downsamples_folder,downsampled_name(slide,1,1))
		flag=slide_1_1+".downsampled"
		if not os.path.isfile(flag):
			run_command(samtools+" sort "+os.path.join(slides_folder,slide+".bam")+" "+slide_1_1+"; "+samtools+" index "+slide_1_1+".bam; touch "+flag)
		for scale in downsamples.keys():
			for repl in range(downsamples[scale]):
				ofile_name=os.path.join(downsamples_folder,downsampled_name(slide,scale,repl+1)) # range generates 0-based
				flag=ofile_name+".downsampled"
				seed1=random.randint(1,100000)
				seed2=random.randint(1,100000)
				if not os.path.isfile(flag): # we do not rewrite
					command=ofile_name+" "+"{}".format(seed1)+" "+"{}".format(seed2)
					print ("Prepare \'"+command+"\'")
	#my $downSAM_string="$downSAM_folder"."downSAM --downSAM.one_from_reads $downmult --downSAM.random_state_file $random_state_file --downSAM.sample_id_postfix $sample_id_postfix < $alingment_file_name.sam | $samtools_folder"."samtools view -Sbh -  >  $alingment_file_name_local.u.bam ";
	#system($downSAM_string) == 0 or die ("Downsampling failed: $?\n");
	#print("#Sorting ... ");
	#system("$samtools_folder"."samtools sort $alingment_file_name_local.u.bam $alingment_file_name_local")  == 0 or die ("Samtools sort failed: $?\n") ;
	#unlink "$alingment_file_name_local.u.bam";
	#print("indexing ... ");
	#system("$samtools_folder"."samtools index $alingment_file_name_local.bam")  == 0 or die ("Samtools index failed: $?\n") ;
	#print "done.\n";
	#
	print()
	#and run it all through our pooling system
	#wait for rhem all to return
	#let's make a list of command for bcf
	#and pool them
	#and wait
	#see you!

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

