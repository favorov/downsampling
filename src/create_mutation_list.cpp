/****************************************************************************\
mutation-call-by-coverage
$Id$
\****************************************************************************/
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>


#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>

#include "Sequences.hpp"
#include "mutation.hpp"
#include "cov_mut_config.hpp"

extern "C"
{
	#include "Random.h"
	#include "confread.h"
}

#define MUT_LIST_POSTFIX "mutation-list"
#define READS_POSTFIX "reads" 
#define ADD_MUT_INFO true

using namespace std;

int main(int argc, char ** argv)
{
	if (
		argc!=2 
		||
		!strcmp(argv[1],"-?") 
		||
		!strcmp(argv[1],"-h")
		||
		!strcmp(argv[1],"-help") 
		||
		!strcmp(argv[1],"--help") 
	)
	{
		cout<<"create_mutation_list configfile"<<endl;
		cout<<"It is a part of mutation-call-by-coverage project."<<endl;
	}
	
	try {
		config_parameters config(argv[1]);

		cout<<config;
		
		rinit(config.random_seed_1,config.random_seed_2);

		SequencesPile sp;

		cout<<"Reading fasta..."<<flush;

		ifstream fasta_stream(config.fasta_file.c_str());
		if (!fasta_stream.good()) {throw * new IOStreamException("Cannot open fasta file for read.\n");}
		fasta_stream>>sp;
		fasta_stream.close();

		cout<<" done\n"<<flush;

		size_t lower_pos=0,upper_pos=sp[0].size()-1;
		//lower and upper non-N position in the sequence
		//TBCIMC (To Be Changed If Multiple Chromosomes)
		
		while(sp[0][lower_pos]==Atgc::atgc2ushort('n')) lower_pos++;
		while(sp[0][upper_pos]==Atgc::atgc2ushort('n')) upper_pos--;

		cout<<"Atgc interval: "<<lower_pos<<":"<<upper_pos<<endl<<flush; 

		vector<mutation> mumus;
		
		mutation just_a_mut;

		cout<<"Preparing mutations ..."<<flush;
		for (size_t pos=lower_pos;pos<=upper_pos;pos++)
		{
			unsigned int draw=(int)(floorf(uni()*config.nucleotides_per_snv)); //0..nucleotides_per_snv-1
			//copy 1
			if (draw==0)
			{
				mumus.push_back(just_a_mut);
				mumus.back().chr=config.chromosome_name;
				mumus.back().pos=pos;
				mumus.back().wild=sp[0][pos];
				mumus.back().copy=1;
				mumus.back().mutate();
			}
			draw=(int)(floorf(uni()*config.nucleotides_per_snv)); //0..nucleotides_per_snv-1
			//copy 2
			if (draw==0)
			{
				mumus.push_back(just_a_mut);
				mumus.back().chr=config.chromosome_name;
				mumus.back().pos=pos;
				mumus.back().wild=sp[0][pos];
				mumus.back().copy=2;
				mumus.back().mutate();
			}
		}

		cout<<" done\n"<<flush;
		cout<<"Writing mutations ..."<<flush;
		ofstream mstream(config.mutations_file.c_str());
		copy(mumus.begin(), mumus.end(), std::ostream_iterator<mutation>(mstream, "\n"));
		mstream.close();
	
		cout<<" done\n"<<flush;
		cout<<"Preparing the read starts  ..."<<flush;
		size_t reads_number=config.read_coverage*(upper_pos-lower_pos)/config.read_length;

		vector<size_t> reads(reads_number);

		for (vector<size_t>::iterator read=reads.begin();read<reads.end();read++)
			*read=lower_pos+(int)(floorf(uni()*(upper_pos-config.read_length+1-lower_pos)));

		sort(reads.begin(),reads.end());
		
		cout<<" done\n"<<flush;

		cout<<"Sequencing ("<<reads_number<<" reads) ..."<<flush;
		
		unsigned long reads_counter=0;

		vector<mutation>::iterator lower_mut=mumus.end();
		vector<mutation>::iterator upper_mut=mumus.begin();
		ofstream rstream(config.reads_file.c_str());
		string conv_string(config.read_length,'n');
		bool initialized=false;
		for (vector<size_t>::iterator read=reads.begin();read<reads.end();read++)
		{
			
			while( upper_mut<mumus.end() && upper_mut->pos<(*read)+config.read_length) upper_mut++; 
			//it is the end() of the read's range mutations 
			if (!initialized)//lower_mut==mumus.end()
			{
				if (mumus.begin()->pos < (*read)+config.read_length) 
				{
					lower_mut=mumus.begin();
					initialized=true;
				}
				//init lower_mut when it is below the end of any (first potentially mutated) read
			}
			else 
				while
					( 
						lower_mut < mumus.end() 
						&& 
						lower_mut->pos < *read 
					) lower_mut++; 
			//it is the first mutation in the read's range
			vector<ushort> read_seq;
			vector<ushort>::iterator read_segment=sp[0].begin()+(*read);
			copy(read_segment,read_segment+config.read_length,back_inserter(read_seq));
			rstream<<">"<<config.chromosome_name<<":"<<*read;
			ushort copy_id=(int)(floorf(uni()*2))+1; //1 or 2
			rstream<<":"<<copy_id;
			if (lower_mut<upper_mut) rstream<<"#";
			copy(lower_mut,upper_mut,ostream_iterator<mutation>(rstream,"#"));
			rstream<<endl;
			for(vector<mutation>::iterator mut=lower_mut;mut<upper_mut;mut++)
				if (mut->copy==copy_id) apply(*mut,read_seq,*read,copy_id);
			Atgc::ushortv2string(read_seq,conv_string);
			//copy(read_seq.begin(),read_seq.end(),ostream_iterator<ushort>(rstream,""));
			rstream<<conv_string<<endl;
			reads_counter++;
			if (!(reads_counter % 100000)) 
			{
				cout<<" "<<reads_counter;
				if (!(reads_counter % 1000000))
					cout<<" of "<<reads_number;
				cout<<" ..."<<flush;
			}
		}
		rstream.close();
		cout<<" done\n"<<flush;
		//sort(mumus.begin(),mumus.end());

		//o.open("mutss");
		//copy(mumus.begin(), mumus.end(), std::ostream_iterator<mutation>(o, ""));
		//o.close();
	} catch (DumbException & e) {cout<<e;return 1;}

	return 0;
}

