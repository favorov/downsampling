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
2:2
5:5
10:10
[flow]
cores:16
random_seed=circumambulate
id=test_run
[reference]
chr1_gl000192_random.fa.gz
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
		fullslidename=os.path.join(slides_folder,slide)
		if not os.path.exists(fullslidename):
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
				

	#flow section
	if "flow" not in config.sections():
		print("No flow section section in "+sys.argv[1]+" . I suppose 2 cores, id=\"test_run\" and random_seed is \"circumambulate\". Is it OK?")
		cores=2
		random_seed="circumambulate"
		id="test_run"
	else:
		if config["flow"].get("cores") == None:
			print("No cores value in flow section section in "+sys.argv[1]+" . I suppose 2 cores. Is it OK?")
			cores=2
		else:
			try:
				cores_string=config.get("flow","cores")
				cores=int(cores_string)
				cores+1 + 1 #test for int, do nothing if OK
			except:
				print("Cores value "+cores_string+" is not an integer. I suppose 2 cores. Is it OK?")
				cores=2
		if config["flow"].get("random_seed") == None:
			print("No random_seed value in flow section section in "+sys.argv[1]+" . I suppose it is \"circumambulate\". Is it OK?")
			random_seed="circumambulate"
		else:
			random_seed=config.get("flow","random_seed")
		
		if config["flow"].get("id") == None:
			print("No id value in flow section section in "+sys.argv[1]+" . I suppose it is \"test_run\". Is it OK?")
			id="test_run"
		else:
			id=config.get("flow","id")
	#cores,id and random seed set


	#reference
	if "reference" not in config.sections():
		print ("Cannot work without reference ([reference])\n")
		sys.exit(1)
	ref=config.options("reference")
	if not len(ref)==1:
		print ("I need one reference reference in [reference] section\n")
		sys.exit(1)
	reference=ref[0]
	if not os.path.isfile(reference):
		print ("Reference file \""+reference+"\" does not exist.\n")
		sys.exit(1)
	#reference exists

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

	print("id=",id)
	print("slide names=",slide_names)
	print("downsamplin shedule=",downsamples)
	print("downSAM=",downSAM)
	print("samtools=",samtools)
	print("bcftools=",bcftools)
	print("cores=",cores)
	print("slides folder=",slides_folder)
	print("bcfs folder=",bcfs_folder)
	print("downsamples folder=",downsamples_folder)
	print("reference=",reference)

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
		if not if_bam[i] and not os.path.isfile(os.path.join(slides_folder,slide_names[i]+".bam")):
			commands.append("cd "+slides_folder+"; "+samtools+" view -Sbh "+slide_names[i]+".sam > "+slide_names[i]+".bam")
	#cd slides_folder; samtools view -Sbh slide.sam > slide.bam	
	if len(commands)>0:
		pool.map(run_command,commands)
	pool.close()
	pool.join()
	del(pool)
	sys.stdout.flush()
	commands[:]=[] #clean commands
	#sams to bams converted
	for slide in slide_names:
	#first, we copy slide to downsamples_folder with _down_by_1_repl_1
	#sort it and index it
		slide_1_1=os.path.join(downsamples_folder,downsampled_name(slide,1,1))
		flag=slide_1_1+".downsampled"
		index_name=slide_1_1+".bam.bai"
		if os.path.isfile(flag) and ((not os.path.isfile(index_name)) or os.stat(index_name).st_size==0):
			os.unlink(flag) # if index is bad, redo
		if not os.path.isfile(flag):
			run_command(samtools+" sort "+os.path.join(slides_folder,slide+".bam")+" "+slide_1_1+"; "+samtools+" index "+slide_1_1+".bam; touch "+flag)
		#Random seeding logic:
		#we start each downsample with a new seed (--downSAM.random_seed_1 and 2)
		#the seed is obtained from python random
		#python random for each downsampling scale and slide in inited with random_seed+"_"+slide_name+"_down_"+str(scale)

		#so, each scale has its own generator history.
		#each scale is reproducible; its results does not depend on other scales
		#each scale is extesible: if we already has some downsamples and ther increase repeats for this scale, 
		#the old ones will remain, so we are not to rerun it.

		for scale in sorted(downsamples.keys()):
			random_seed_loc=random_seed+"_"+slide+"_d_"+str(scale)
			random.seed(random_seed_loc)
			for repl in range(downsamples[scale]):
				sample_id_postfix="-ds"+str(scale)+"-r"+str(repl+1)
				ofile_name=os.path.join(downsamples_folder,downsampled_name(slide,scale,repl+1)) # range generates 0-based
				flag=ofile_name+".downsampled"
				seed1=str(random.randint(1,1000000))
				seed2=str(random.randint(1,1000000))
				index_name=ofile_name+".bam.bai"
				if os.path.isfile(flag) and ((not os.path.isfile(index_name)) or os.stat(index_name).st_size==0):
					os.unlink(flag) # if index is bad, redo
				if not os.path.isfile(flag): # we do not rewrite
					command=samtools+" view -h "+slide_1_1+".bam | "+downSAM+" --downSAM.one_from_reads "+str(scale)+" --downSAM.random_seed_1 "+seed1+" --downSAM.random_seed_2 "+seed2+" --downSAM.sample_id_postfix "+sample_id_postfix+" | samtools view -Sbh - > "+ofile_name+".bam && "+samtools+" index "+ofile_name+".bam && touch "+flag  
					#print ("Prepare \'"+command+"\'")
					commands.append(command)
	pool=Pool(cores)
	if len(commands)>0:
		pool.map(run_command,commands)
	#and run it all through our pooling system
	#wait for rhem all to return
	pool.close()
	pool.join()
	del(pool)
	sys.stdout.flush()
	commands[:]=[] #clean commands
	#bams downsampled
	#and now, bcfs.....
	downsamples[1]=1 # to call original in standard framework
	for scale in sorted(downsamples.keys()):
		for repl in range(downsamples[scale]):
			bamliststring=" "
			bcffilename=os.path.join(bcfs_folder,downsampled_name(id,scale,repl+1)+".bcf")
			flag=os.path.join(bcfs_folder,downsampled_name(id,scale,repl+1)+".called")

			if not os.path.isfile(flag): # we do not rewrite
				for slide in slide_names:
					bampath=os.path.join(downsamples_folder,downsampled_name(slide,scale,repl+1)+".bam")
					bamliststring=bamliststring+bampath+" "
				command=samtools+" mpileup -uf "+reference+bamliststring+" | bcftools view -bcvg - > "+bcffilename+" && touch "+flag 
				commands.append(command)
	pool=Pool(cores)
	if len(commands)>0:
		pool.map(run_command,commands)
	#and run it all through our pooling system
	#wait for rhem all to return
	pool.close()
	pool.join()
	del(pool)
	sys.stdout.flush()
	commands[:]=[] #clean commands
	print()
	#and run it all through our pooling system
	#wait for rhem all to return
	#let's make a list of command for bcf
	#and pool them
	#and wait
	#see you!

	sys.exit(0)


#here, we finally run it all :)
if __name__ == "__main__":
    main()

