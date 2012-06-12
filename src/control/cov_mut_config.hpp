/****************************************************************************\
mutation-call-by-coverage
$Id: Sequences.hpp 1014 2009-03-01 16:50:36Z favorov $
\****************************************************************************/

#ifndef COV_MUT_CONFIG_HPP
#define COV_MUT_CONFIG_HPP

#define SEED_1 1248312
#define SEED_2 7436111

extern "C"
{
	#include "confread.h"
}

#include <string>
#include <stdio.h>
#include <iostream>
#include <iomanip>

struct config_parameters
{
	std::string fasta_file;
	std::string chromosome_name;
	unsigned int nucleotides_per_snv;
	unsigned int read_length;	
	unsigned int read_coverage;
	std::string mutations_file;
	std::string reads_file;
	unsigned int random_seed_1,random_seed_2; 
	config_parameters():
		fasta_file(""),
		chromosome_name(""),
		nucleotides_per_snv(1000),
		read_length(100),
		read_coverage(100),
		mutations_file("mutations"),
		reads_file("reads"),
		random_seed_1(SEED_1),
		random_seed_2(SEED_2){};
	config_parameters(const char * cfilename) throw (DumbException,IOStreamException):
		fasta_file(""),
		chromosome_name(""),
		nucleotides_per_snv(1000),
		read_length(100),
		read_coverage(100),
		mutations_file("mutations"),
		reads_file("reads"),
		random_seed_1(SEED_1),
		random_seed_2(SEED_2)
	{
		unsigned int leng=999;
		char str[leng+1];
		int res;
		FILE * cfile=fopen(cfilename,"r");
		if (!cfile)
			throw (*new IOStreamException("File cannot be opened for read.\n"));
		if ((res=ReadConfigString(cfile,"fasta_file",str,leng,obligatory))<=0)
			throw (*new DumbException("No file name in config.\n"));
		fasta_file=str;
		if ((res=ReadConfigString(cfile,"chromosome_name",str,leng,obligatory))<=0)
			throw (*new DumbException("No chromosome name in config.\n"));
		chromosome_name=str;
		if ((res=ReadConfigUnsignedInt(cfile,"nucleotides_per_snv", &nucleotides_per_snv,optional))<0)
			throw (*new DumbException("Something stupid on nucleotides_per_snv read happened.\n"));
		if ((res=ReadConfigUnsignedInt(cfile,"read_length", &read_length,optional))<0)
			throw (*new DumbException("Something stupid on read_length read happened.\n"));
		if ((res=ReadConfigUnsignedInt(cfile,"read_coverage", &read_coverage,optional))<0)
			throw (*new DumbException("Something stupid on read_coverage read happened.\n"));
		strcpy(str,mutations_file.c_str());
		if ((res=ReadConfigString(cfile,"mutations",str,leng,optional))<0)
			throw (*new DumbException("Something stupid happened when read the mutations file name.\n"));
		mutations_file=str;
		strcpy(str,reads_file.c_str());
		if ((res=ReadConfigString(cfile,"reads",str,leng,optional))<0)
			throw (*new DumbException("Something stupid happened when read the reads file name.\n"));
		reads_file=str;
		if ((res=ReadConfigUnsignedInt(cfile,"random_seed_1", &random_seed_1,optional))<0)
			throw (*new DumbException("Something stupid on random_seed_1 read happened.\n"));
		if ((res=ReadConfigUnsignedInt(cfile,"random_seed_2", &random_seed_2,optional))<0)
			throw (*new DumbException("Something stupid on random_seed_2 read happened.\n"));

	}
};

inline
ostream & operator<< (ostream & os, const config_parameters & cp) 
{
	os<<"fasta_file"<<"="<<cp.fasta_file<<endl;
	os<<"chromosome_name"<<"="<<cp.chromosome_name<<endl;
	os<<"nucleotides_per_snv"<<"="<<cp.nucleotides_per_snv<<endl;
	os<<"read_length"<<"="<<cp.read_length<<endl;
	os<<"read_coverage"<<"="<<cp.read_coverage<<endl;
	os<<"mutations"<<"="<<cp.mutations_file<<endl;
	os<<"reads"<<"="<<cp.reads_file<<endl;
	os<<"random_seed_1"<<"="<<cp.random_seed_1<<endl;
	os<<"random_seed_2"<<"="<<cp.random_seed_2<<endl;
	return os;
}

#endif

