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

#include <boost/random/ranlux.hpp>
#include <boost/random/uniform_int_distribution.hpp>
#include <boost/random/seed_seq.hpp>

#include <boost/iostreams/filtering_streambuf.hpp>
#include <boost/iostreams/filter/gzip.hpp>

#include "Sequences.hpp"
#include "mutation.hpp"
#include "cheapseq_config.hpp"

#define MUT_LIST_POSTFIX "mutation-list"
#define READS_POSTFIX "reads" 
#define ADD_MUT_INFO true

boost::random::ranlux64_4 gen;

//generator is to be the only

using namespace std;

int main(int argc, char ** argv)
{
	try {
		config_parameters config(argc,argv);

		cout<<config;
		
		std::vector<unsigned long> iniseed(2);
		iniseed[0]=config.random_seed_1;
		iniseed[1]=config.random_seed_2;
		boost::random::seed_seq iniseedseq(iniseed);
		gen.seed(iniseedseq);

		SequencesPile sp;

		if (config.fasta_file.length()<2)
			{throw * new DumbException("Too short or empty fasta file name.\n");}

		if (!config.fasta_file.substr(config.fasta_file.length()-2,2).compare("gz"))
		{
			cout<<"Opening gzipped fasta..."<<flush;
			ifstream fastagzfile(config.fasta_file.c_str(), ios_base::in | ios_base::binary);
			if (!fastagzfile.good()) {throw * new IOStreamException("Cannot open gzipped fasta file for read.\n");}
			boost::iostreams::filtering_streambuf<boost::iostreams::input> in;
			in.push(boost::iostreams::gzip_decompressor());
			in.push(fastagzfile);
			istream fasta_stream(&in);
			cout<<" Reading gzipped fasta..."<<flush;
			fasta_stream>>sp;
			fastagzfile.close();
		}
		else
		{
			cout<<"Opening fasta..."<<flush;
			ifstream fasta_stream(config.fasta_file.c_str());
			if (!fasta_stream.good()) {throw * new IOStreamException("Cannot open fasta file for read.\n");}
			cout<<" Reading fasta..."<<flush;
			fasta_stream>>sp;
			fasta_stream.close();
		}

		cout<<" done.\n"<<flush;

		size_t lower_index=0,upper_index=sp[0].size()-1;
		//lower and upper non-N indices in the sequence
		//position=index+1
		//TBCIMC (To Be Changed If Multiple Chromosomes)
		
		while(sp[0][lower_index]==Atgc::atgc2ushort('n')) lower_index++;
		while(sp[0][upper_index]==Atgc::atgc2ushort('n')) upper_index--;

		cout<<"Atgc interval: "<<lower_index+1<<":"<<upper_index+1<<endl<<flush; 
		
		// 0 - based

		vector<mutation> mumus;
		
		mutation just_a_mut;

		cout<<"Preparing mutations ..."<<flush;
    boost::random::uniform_int_distribution<unsigned int> dist_mut_prob(0,config.bases_per_snv-1);
		for (size_t pos=lower_index+1;pos<=upper_index+1;pos++)
		{
			//copy 1
			if (dist_mut_prob(gen)==0)
			{
				mumus.push_back(just_a_mut);
				mumus.back().chr=config.chromosome_name;
				mumus.back().pos=pos;
				mumus.back().wild=sp[0][pos-1];
				mumus.back().copy=1;
				mumus.back().mutate();
			}
			//copy 2
			if (dist_mut_prob(gen)==0)
			{
				mumus.push_back(just_a_mut);
				mumus.back().chr=config.chromosome_name;
				mumus.back().pos=pos;
				mumus.back().wild=sp[0][pos-1];
				mumus.back().copy=2;
				mumus.back().mutate();
			}
		}
		//cout<<endl<<last mut is "<<*(mumus.end()-1)<<endl;
		cout<<" done\n"<<flush;
		cout<<"Writing mutations ..."<<flush;
		ofstream mstream(config.mutations_file.c_str());
		copy(mumus.begin(), mumus.end(), std::ostream_iterator<mutation>(mstream, "\n"));
		mstream.close();
	
		cout<<" done\n"<<flush;
		cout<<"Preparing the read starts  ..."<<flush;
		size_t reads_number=config.coverage*(upper_index-lower_index)/config.read_length;

		vector<size_t> read_starts(reads_number);
		//read starts

    boost::random::uniform_int_distribution<size_t> random_read_start(lower_index+1,upper_index-config.read_length+2);
		//starts are 1-based
		for (vector<size_t>::iterator read_start_ptr=read_starts.begin();read_start_ptr<read_starts.end();read_start_ptr++)
			*read_start_ptr=random_read_start(gen);

		sort(read_starts.begin(),read_starts.end());
		
		cout<<" done\n"<<flush;

		cout<<"Sequencing ("<<reads_number<<" reads) ..."<<flush;
		
		unsigned long reads_counter=0;

		vector<mutation>::iterator lower_mut=mumus.end();
		vector<mutation>::iterator upper_mut=mumus.begin();
		ofstream rstream(config.reads_file.c_str());
		string conv_string(config.read_length,'n');
		
		bool initialized=false;
		for (vector<size_t>::iterator read_start_ptr=read_starts.begin();read_start_ptr<read_starts.end();read_start_ptr++)
		{
			
			while( upper_mut<mumus.end() && upper_mut->pos<(*read_start_ptr)+config.read_length) upper_mut++; 
			//it is the end() of the read's range mutations 
			if (!initialized)//lower_mut==mumus.end()
			{
				if (mumus.begin()->pos < (*read_start_ptr)+config.read_length) 
				{
					lower_mut=mumus.begin();
					initialized=true;
				}
				//init lower_mut when it is below the end of any (first potentially mutated) read
			}
			//so, if the first mutation is upper than the current read start, we do not init anything
			//and the mutation cycle will actually be voided because lower_mut==mumus.end()
			//if it is lower, we init the process
			if (initialized)	while ( lower_mut < mumus.end() && lower_mut->pos < *read_start_ptr ) lower_mut++; 
			//it is the first mutation in the read's range
			vector<unsigned short> read_seq;
			vector<unsigned short>::iterator read_segment=sp[0].begin()+(*read_start_ptr)-1;
			copy(read_segment,read_segment+config.read_length,back_inserter(read_seq));
			rstream<<">read"<<reads_counter<<":"<<config.chromosome_name<<":"<<*read_start_ptr;
			boost::random::uniform_int_distribution<int> random_copy(1,2);
			unsigned short copy_id=random_copy(gen); //1 or 2
			rstream<<":"<<copy_id;
			for(vector<mutation>::iterator mut=lower_mut;mut<upper_mut;mut++)
				if (mut->copy==copy_id) 
				{	
					apply(*mut,read_seq,*read_start_ptr,copy_id);
					rstream<<"#"<<mut->pos<<":"<<mut->wild<<"->"<<mut->mutated;
				}
			rstream<<endl;
			Atgc::ushortv2string(read_seq,conv_string);
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
