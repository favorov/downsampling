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
5/2:5
5:5
10:10
[flow]
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
#default is "bcfs"
bcfs:bcfs
#default is .
slides:."""
	print(sample_config)
	return

def write_command(depend,source,command):
	print(depend+":"+source)	
	print("\t"+command)

def fulltoolname(toolname,toolpath=None):
	if toolpath==None or toolpath=="":
	# we will try to find it with which; virtually if it works - it works, no checks needed!
	#but the thing is new, so we will check it
		try:
			resultfulltoolname=os.popen("which "+toolname).read().rstrip()
			if not resultfulltoolname:
				raise Exception("Empty which return") #exception is stupid, I do not know python system of throw/catch
		except:
			print("Which did not find "+toolname+" and its folder is not correctly given in config. So what?",file=sys.stderr)
			sys.exit(1)
	else: #folder is given, we are to add it and to test it
		resultfulltoolname=os.path.join(toolpath,toolname)
		print("------"+resultfulltoolname,file=sys.stderr)
	if not os.path.isfile(resultfulltoolname): #here, we test that file exist
		print("The file "+resultfulltoolname+" does not exist... trying which...",file=sys.stderr)
		return fulltoolname(toolname) #trying which	
	if subprocess.call("[ -x "+resultfulltoolname+" ]",shell=True): 
	#we test that it is exec, the thing return 0 if it is OK
	#if test returned 1, it file is not exec
		print("The file "+resultfulltoolname+" is not executable. ... trying which...",file=sys.stderr)
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

def downsampled_name(name,scale,repl,mult_chance=1):
	if mult_chance==1:
		output_file_name="{}_down_by_{}_repl_{}".format(name,scale,repl)
	else:
		output_file_name="{}_down_by_{}_mult_{}_repl_{}".format(name,scale,mult_chance,repl)
	return output_file_name

def main():
	#vars that define the behaviour of the things
	if_bam=[]
	#boolean, bam or sam for each slide
	#all downsamples are bams, whatever
	slide_names=[]
	#names of slides without extension
	downsample_scales=[]
	downsample_chances_mult=[]
	downsample_repeats=[]
	#downsampling_string is for report		
	downsampling_string=""
	#scales, multipliers and repeats fro each schedule line	
	#folders

	if len(sys.argv)<2:
		my_info()
		sys.exit(0)

	if len(sys.argv)>2:
		print ("\nToo many paraneters!\n",file=sys.stderr)
		sys.exit(1)

	if sys.argv[1] in ["--help","--h","-h","-?","-help"]:
		my_help()
		sys.exit(0)
				
	if sys.argv[1]=="--write-sample-config":
		write_sample_config()
		sys.exit(0)

	if not os.path.exists(sys.argv[1]):
		print ("Cannot open config "+sys.argv[1]+".",file=sys.stderr)
		sys.exit(1)

	config = configparser.ConfigParser(allow_no_value=True)
	config.optionxform = str #to be case-preserveing
	config.read(sys.argv[1])

	logname=sys.argv[1]+'.log'
	sys.stderr = open(logname, 'w')
	print('#Coverage project. \n#We generate makefile for downsamling \n#the configuration file is '+sys.argv[1])
	print('#The log/error messages are in ' +logname)

	#folders for data, slides, etc
	if "folders" not in config.sections():
		print("No folders section section in "+sys.argv[1]+" . I will post defaults:\n \".\" for slides,  \"./bcfs\" for bcfs, \"./downsamples\" for downsamples. Is it OK?",file=sys.stderr)
		slides_folder="."
		bcfs_folder="./bcfs"
		downsamples_folder="./downsamples"
	else:
		if config["folders"].get("slides")==None:
			print("Default value \".\" for the slides folder",file=sys.stderr)
			slides_folder="."
		else:
			slides_folder=config.get("folders","slides")

		if config["folders"].get("downsamples")==None:
			print("Default value \".downsamples\" for the downsamples folder",file=sys.stderr)
			downsamples_folder="./downsamples"
		else:
			downsamples_folder=config.get("folders","downsamples")
			

		if config["folders"].get("bcfs")==None:
			print("Default value \"./bcfs\" for the bcfs folder",file=sys.stderr)
			bcfs_folder="./bcfs"
		else:
			bcfs_folder=config.get("folders","bcfs")


		if config["folders"].get("flags")!=None:
			print("The flags option is obsoleted!",file=sys.stderr)

	make_sure_path_exists(downsamples_folder)
	make_sure_path_exists(bcfs_folder)
	#folders checked
	
	#here, we start to check slides

	if "slides" not in config.sections():
		print("no slides section in "+sys.argv[1]+" .",file=sys.stderr)
		sys.exit(1)

	slides=config.options("slides")


	for slide in slides:
		fullslidename=os.path.join(slides_folder,slide)
		if not os.path.exists(fullslidename):
			print("Cannot open slide: "+fullslidename+" .",file=sys.stderr)
			sys.exit(1)
		#file exist
		if re.search(r"\.bam$",slide):
			if_bam.append(True)
		elif re.search(r"\.sam$",slide):
			if_bam.append(False)
		else:
			print("Unknown slide extension"+slide+"\n",file=sys.stderr)
			sys.exit(1)
		#slide name ok
		slide_names.append(slide[:-4])
		
	#we checked slides and we know bams and sams

	#checkin downsampling
	if "downsampling" not in config.sections():
		print("no downsampling section section in "+sys.argv[1]+" .",file=sys.stderr)
		sys.exit(1)

	for scale_ratio in config.options("downsampling"):
		scale_and_mult=scale_ratio.split("/")
		
		try:
			scale_int=int(scale_and_mult[0])
			scale_int + 1 #test for int, do nothing if OK
		except:
			print("Downsampling scale "+scale_and_mult[0]+" is not an integer.\n",file=sys.stderr)
			sys.exit(1)
		
		if len(scale_and_mult)==1:
			mult_int=1
		elif len(scale_and_mult)==2:
			try:
				mult_int=int(scale_and_mult[1])
				mult_int + 1 #test for int, do nothing if OK
			except:
				print("Sampling chance multiplier "+scale_and_mult[1]+" is not an integer.\n",file=sys.stderr)
				sys.exit(1)
		elif len(scale_and_mult)>2:
			print("sampling scale "+scale_ratio+" is nor an integer niether a natural ratio.\n",file=sys.stderr)
			sys.exit(1)
		
		repeats=config["downsampling"][scale_ratio]
		try:
			repeats=int(repeats)
			repeats + 1 #test for int, do nothing if OK
		except:
			print("Downsampling repeats at scale "+scale_ratio+" is "+repeats+" and it is not an integer.\n",file=sys.stderr)
			sys.exit(1)

		downsample_scales.append(scale_int)
		downsample_chances_mult.append(mult_int)
		downsample_repeats.append(repeats)
		downsample_string=str(scale_int)
		if mult_int>1:
			downsample_string=downsample_string+"/"+str(mult_int)
		downsample_string=downsample_string+":"+str(repeats)+" "

		#downsampling_string is for report		

	#flow section
	if "flow" not in config.sections():
		print("No flow section section in "+sys.argv[1]+" . I suppose, id=\"test_run\" and random_seed is \"circumambulate\". Is it OK?",file=sys.stderr)
		random_seed="circumambulate"
		id="test_run"
	else:
		if config["flow"].get("cores") != None:
			print("The core value is obsoleted; it will be controlled by the system that run the makefile.",file=sys.stderr)
		if config["flow"].get("random_seed") == None:
			print("No random_seed value in flow section section in "+sys.argv[1]+" . I suppose it is \"circumambulate\". Is it OK?",file=sys.stderr)
			random_seed="circumambulate"
		else:
			random_seed=config.get("flow","random_seed")
		
		if config["flow"].get("id") == None:
			print("No id value in flow section section in "+sys.argv[1]+" . I suppose it is \"test_run\". Is it OK?",file=sys.stderr)
			id="test_run"
		else:
			id=config.get("flow","id")
	#cores,id and random seed set


	#reference
	if "reference" not in config.sections():
		print ("Cannot work without reference ([reference])\n",file=sys.stderr)
		sys.exit(1)
	ref=config.options("reference")
	if not len(ref)==1:
		print ("I need one reference reference in [reference] section\n",file=sys.stderr)
		sys.exit(1)
	reference=ref[0]
	if not os.path.isfile(reference):
		print ("Reference file \""+reference+"\" does not exist.\n",file=sys.stderr)
		sys.exit(1)
	#reference exists

	#executable programs
	if "tool_paths" not in config.sections():
		print("No tool_paths section section in "+sys.argv[1]+" . Is it OK?",file=sys.stderr)
		samtools=fulltoolname('samtools')
		downSAM=fulltoolname('downSAM')
		bcftools=fulltoolname('bcftools')
	else:	
		samtools=fulltoolname('samtools',config["tool_paths"].get("samtools"))
		downSAM=fulltoolname('downSAM',config["tool_paths"].get("downSAM"))
		bcftools=fulltoolname('bcftools',config["tool_paths"].get("bcftools"))
	#executable programs set

	print("id=",id,file=sys.stderr)
	print("slide names=",slide_names,file=sys.stderr)
	print("downsampling shedule=",downsampling_string,file=sys.stderr)
	print("downSAM=",downSAM,file=sys.stderr)
	print("samtools=",samtools,file=sys.stderr)
	print("bcftools=",bcftools,file=sys.stderr)
	#print("cores=",cores,file=sys.stderr)
	print("slides folder=",slides_folder,file=sys.stderr)
	print("bcfs folder=",bcfs_folder,file=sys.stderr)
	print("downsamples folder=",downsamples_folder,file=sys.stderr)
	print("reference=",reference,file=sys.stderr)

	# we know everything
	#lets do something
	#if a file exist 
	#and it is not zero-length
	#we do not generate the command
	#let's make a list of commands to downsample
	
	#at very first, we write the makefile preabule

	print(".PHONY: all")
	
	downsample_scales.insert(0,1) # to mention original in standard framework
	downsample_chances_mult.insert(0,1) 
	downsample_repeats.insert(0,1)

	#now, we list all the bcfs as all
	
	bcfs=[]
	for scale_no in range(len(downsample_scales)):
		for repl in range(downsample_repeats[scale_no]):
			shortfilename=downsampled_name(id,downsample_scales[scale_no],repl+1,downsample_chances_mult[scale_no])
			bcffilename=os.path.join(bcfs_folder,shortfilename+".bcf")
			bcfs.append('\t'+bcffilename+' ')
	print("all: \\")
	print ("\\\n".join(bcfs))
	print()	
	#bcfs needs downsampled slides;
	#the slides were dowmsampled separately, now we 
	#join them 'horizontally' to bake the base calling
	#each of the bcfs is generated from the list of downasamples
	#with the same id and ratio, but from differend slides
	print("#bcfs need downsamples")
	for scale_no in range(len(downsample_scales)):
		for repl in range(downsample_repeats[scale_no]):
			bamliststring=" "
			shortfilename=downsampled_name(id,downsample_scales[scale_no],repl+1,downsample_chances_mult[scale_no])
			bcffilename=os.path.join(bcfs_folder,shortfilename+".bcf")
			for slide in slide_names:
				bampath=os.path.join(downsamples_folder,downsampled_name(slide,downsample_scales[scale_no],repl+1,downsample_chances_mult[scale_no])+".bam")
				bamliststring=bamliststring+bampath+" "
			command=samtools+" mpileup -uf "+reference+bamliststring+" | "+bcftools+" view -bcvg - > "+bcffilename
			print(bcffilename+": "+bamliststring)
			print("\t"+command)
	print()	
	#downsamples need downsampling from sams

	#Let's speak about how we get downsamles. It needs a sorted version of each slide (slide_1_1) 
	#
	#Random seeding logic:
	#we start each downsample with a new seed (--downSAM.random_seed_1 and 2)
	#the seed is obtained from python random
	#python random for each downsampling scale and slide in inited with random_seed+"_"+slide_name+"_d_"+str(scale)+"_m_"+str(multiplier)

	#so, each scale has its own generator history.
	#each scale is reproducible; its results does not depend on other scales
	#each scale is extesible: if we already has some downsamples and ther increase repeats for this scale, 
	#the old ones will remain, so we are not to rerun it.

	for slide in slide_names:
		slide_1_1_short=downsampled_name(slide,1,1)
		slide_1_1=os.path.join(downsamples_folder,slide_1_1_short)

		for scale_no in range(len(downsample_scales)):
			scale=downsample_scales[scale_no]
			mult=downsample_chances_mult[scale_no]
			if scale==1: continue
			random_seed_loc=random_seed+"_"+slide+"_d_"+str(scale)+"_m_"+str(mult)
			random.seed(random_seed_loc)
			for repl in range(downsample_repeats[scale_no]):
				if mult==1:
					sample_id_postfix="-ds="+str(scale)+"/"+str(mult)+"-r="+str(repl+1)
				ofile_short_name=downsampled_name(slide,scale,repl+1,mult)
				ofile_name=os.path.join(downsamples_folder,ofile_short_name) # range generates 0-based
				seed1=str(random.randint(1,1000000))
				seed2=str(random.randint(1,1000000))
				#index_name=ofile_name+".bam.bai"
				print(ofile_name+".bam: "+slide_1_1+".bam")
				command=samtools+" view -h "+slide_1_1+".bam | "+downSAM+" --downSAM.one_from_reads "+str(scale)+"--downSAM.chances_multiplier"+str(mult)+" --downSAM.random_seed_1 "+seed1+" --downSAM.random_seed_2 "+seed2+" --downSAM.sample_id_postfix "+sample_id_postfix+" | " +samtools+" view -Sbh - > "+ofile_name+".bam"
				print ("\t"+command)
	print()	
	
	#now, original files to downsample. They are just copied from slides folder and sorted
	for slide in slide_names:
		slide_1_1_short=downsampled_name(slide,1,1)
		slide_1_1=os.path.join(downsamples_folder,slide_1_1_short)
		#index_name=slide_1_1+".bam.bai"
		origslide=os.path.join(slides_folder,slide+".bam")
		print(slide_1_1+".bam: "+origslide)
		command=samtools+" sort "+origslide+" "+slide_1_1
		print ("\t"+command)
	
	#if the original is sam, first turn it to bam
	for i in range(0,len(if_bam)):
		if not if_bam[i] and not os.path.isfile(os.path.join(slides_folder,slide_names[i]+".bam")):
			print(slide_names[i]+".bam: "+slide_names[i]+".sam")
			command="cd "+slides_folder+"; "+samtools+" view -Sbh "+slide_names[i]+".sam > "+slide_names[i]+".bam"
			print ("\t"+command)

	sys.stderr.close()
	sys.exit(0)


#here, we finally run it all :)
if __name__ == "__main__":
    main()

