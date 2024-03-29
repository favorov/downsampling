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
#default is "downsamples"
downsamples:downsamples
#default is "pileups"
pileups:pileups
#default is "bcfs"
bcfs:bcfs
#deafuult is .flags
flags: .bcfs
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
	config.optionxform = str #to be case-preserveing
	config.read(sys.argv[1])

	#folders for data, slides, etc
	if "folders" not in config.sections():
		print("No folders section section in "+sys.argv[1]+" . I will post defaults:\n \".\" for slides, \"./pileups\" for pileups,  \"./.flags\" for flags , \"./bcfs\" for bcfs, \"./downsamples\" for downsamples. Is it OK?")
		slides_folder="."
		pileups_folder="./pileups"
		bcfs_folder="./bcfs"
		downsamples_folder="./downsamples"
		flags_folder="./.flags"
	else:
		if config["folders"].get("slides")==None:
			print("Defult value \".\" for the slides folder")
			slides_folder="."
		else:
			slides_folder=config.get("folders","slides")

		if config["folders"].get("downsamples")==None:
			print("Defult value \".downsamples\" for the downsamples folder")
			downsamples_folder="./downsamples"
		else:
			downsamples_folder=config.get("folders","downsamples")
			

		if config["folders"].get("bcfs")==None:
			print("Defult value \"./bcfs\" for the bcfs folder")
			bcfs_folder="./bcfs"
		else:
			bcfs_folder=config.get("folders","bcfs")


		if config["folders"].get("pileups")==None:
			print("Defult value \"./pileups\" for the pileups folder")
			pileups_folder="./pileups"
		else:
			pileups_folder=config.get("folders","pileups")

		if config["folders"].get("flags")==None:
			print("Defult value \"./.flags\" for the pileups folder")
			flags_folder="./.flags"
		else:
			flags_folder=config.get("folders","flags")

	make_sure_path_exists(downsamples_folder)
	make_sure_path_exists(bcfs_folder)
	make_sure_path_exists(pileups_folder)
	make_sure_path_exists(flags_folder)
	#folders checked
	
	#here, we start to check slides

	if "slides" not in config.sections():
		print("no slides section in "+sys.argv[1]+" .")
		sys.exit(1)

	slides=config.options("slides")


	for slide in slides:
		fullslidename=os.path.join(slides_folder,slide)
		if not os.path.exists(fullslidename):
			print("Cannot open slide: "+fullslidename+" .")
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
	print("pileups folder=",pileups_folder)
	print("bcfs folder=",bcfs_folder)
	print("downsamples folder=",downsamples_folder)
	print("flags folder=",flags_folder)
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
		slide_1_1_short=downsampled_name(slide,1,1)
		slide_1_1=os.path.join(downsamples_folder,slide_1_1_short)
		flag=os.path.join(flags_folder,slide_1_1_short+".sorted")
		index_name=slide_1_1+".bam.bai"
		if os.path.isfile(flag) and ((not os.path.isfile(index_name)) or os.stat(index_name).st_size==0):
			os.unlink(flag) # if index is bad, redo
		if not os.path.isfile(flag):
			commands.append(samtools+" sort "+os.path.join(slides_folder,slide+".bam")+" "+slide_1_1+"; "+samtools+" index "+slide_1_1+".bam; touch "+flag)
	pool=Pool(cores)
	if len(commands)>0:
		pool.map(run_command,commands) #sorting slides
	#and run it all through our pooling system
	#wait for rhem all to return
	pool.close()
	pool.join()
	del(pool)
	sys.stdout.flush()
	commands[:]=[] #clean commands
	#slides are sorted
	#Random seeding logic:
	#we start each downsample with a new seed (--downSAM.random_seed_1 and 2)
	#the seed is obtained from python random
	#python random for each downsampling scale and slide in inited with random_seed+"_"+slide_name+"_down_"+str(scale)

	#so, each scale has its own generator history.
	#each scale is reproducible; its results does not depend on other scales
	#each scale is extesible: if we already has some downsamples and ther increase repeats for this scale, 
	#the old ones will remain, so we are not to rerun it.

	for slide in slide_names:
		slide_1_1_short=downsampled_name(slide,1,1)
		slide_1_1=os.path.join(downsamples_folder,slide_1_1_short)
		for scale in sorted(downsamples.keys()):
			random_seed_loc=random_seed+"_"+slide+"_d_"+str(scale)
			random.seed(random_seed_loc)
			for repl in range(downsamples[scale]):
				sample_id_postfix="-ds"+str(scale)+"-r"+str(repl+1)
				ofile_short_name=downsampled_name(slide,scale,repl+1)
				ofile_name=os.path.join(downsamples_folder,ofile_short_name) # range generates 0-based
				flag=os.path.join(flags_folder,ofile_short_name+".downsampled")
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
	#and now, pileups.....
	downsamples[1]=1 # to call original in standard framework
	for scale in sorted(downsamples.keys()):
		for repl in range(downsamples[scale]):
			bamliststring=" "
			shortfilename=downsampled_name(id,scale,repl+1)
			pileupfilename=os.path.join(pileups_folder,shortfilename+".pileup.gz")
			flag=os.path.join(flags_folder,shortfilename+".pileuped")

			if not os.path.isfile(flag): # we do not rewrite
				for slide in slide_names:
					bampath=os.path.join(downsamples_folder,downsampled_name(slide,scale,repl+1)+".bam")
					bamliststring=bamliststring+bampath+" "
				command=samtools+" mpileup -uf "+reference+bamliststring+" | gzip -c > "+pileupfilename+" && touch "+flag 
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
	#and run it all through our pooling system
	#wait for rhem all to return
	#let's make a list of command for bcf
	#and pool them
	#and wait
	#see you!
	#and now, bcfs.....
	downsamples[1]=1 # to call original in standard framework
	for scale in sorted(downsamples.keys()):
		for repl in range(downsamples[scale]):
			shortfilename=downsampled_name(id,scale,repl+1)
			pileupfilename=os.path.join(pileups_folder,shortfilename+".pileup.gz")
			bcffilename=os.path.join(bcfs_folder,shortfilename+".bcf")
			flag=os.path.join(flags_folder,shortfilename+".called")

			if not os.path.isfile(flag): # we do not rewrite
				command="gzip -dc "+pileupfilename+" | "+bcftools+" view -bcvg - > "+bcffilename+" && touch "+flag 
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

	sys.exit(0)


#here, we finally run it all :)
if __name__ == "__main__":
    main()

