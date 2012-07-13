/****************************************************************************\
mutation-call-by-coverage
$Id$
\****************************************************************************/
#include <string>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <boost/program_options.hpp>
#include <boost/random/ranlux.hpp>
#include <boost/random/uniform_int_distribution.hpp>
#include <boost/random/seed_seq.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>

#define NSEED_1 2732596
#define NSEED_2 6596412

boost::random::ranlux64_4 gen;
//generator is to be the only

using namespace std;

const char * atgc = "atgc";

int main(int argc, char ** argv)
{
	unsigned int bases_per_error;
	unsigned int random_seed_1;
	unsigned int random_seed_2;
	boost::program_options::options_description desc
			("Noiser: adds noise to FastA/Q, outputs Fasta.\nNoise is uniformaly distributed random bases.\n   Command-line options override config file;\n   section.option is the same as option in [section].\n Options (config file lines)");
	desc.add_options()
			("help", "help")
			("config-file", boost::program_options::value<string>(), "configuration file name")
			("noiser.bases_per_error", boost::program_options::value<unsigned int>(&bases_per_error)->default_value(0), "one noise error is expected per this number of bases; defaut is no noise")
			("noiser.random_seed_1", boost::program_options::value<unsigned int>(&random_seed_1)->default_value(NSEED_1), "random seed 1 for noiser")
			("noiser.random_seed_2", boost::program_options::value<unsigned int>(&random_seed_2)->default_value(NSEED_2), "random seed 2 for noiser")
	;
	try { 
		boost::program_options::positional_options_description pd; 
		pd.add("config-file", -1);
		boost::program_options::variables_map vm;
		boost::program_options::store(boost::program_options::command_line_parser(argc, argv).options(desc).positional(pd).run(), vm);

		//boost::program_options::notify(vm);

		if (vm.count("help")) {
			cout << desc << "\n";
			return 0;	
		}

		if (vm.count("config-file")) 
		{
			ifstream conf(vm["config-file"].as<string>().c_str());
			if (!conf)
			{
				cout<<"File \""<<vm["config-file"].as<string>().c_str()<<"\" cannot be opened for read.\n";
				return 1;
			}
			boost::program_options::store(boost::program_options::parse_config_file(conf, desc, true), vm);
		}

		boost::program_options::notify(vm);
	
	} catch( const exception& e)
	{
			cout<<e.what()<<endl<<desc<<endl;
	}

	std::vector<unsigned long> iniseed(2);
	iniseed[0]=random_seed_1;
	iniseed[1]=random_seed_2;
	boost::random::seed_seq iniseedseq(iniseed);
	gen.seed(iniseedseq);

	boost::random::uniform_int_distribution<unsigned int> dist_error_prob(0,bases_per_error-1);
	boost::random::uniform_int_distribution<unsigned int> error_base(0,3);

	string current_string;



	bool in_fastq_block=false, in_fasta_block=false;
	unsigned short in_block_counter=0;
	string seq_id;

	while (!cin.eof())
	{
		getline(cin, current_string);
		boost::trim(current_string);
		// cout<<current_string<<"*"<<endl; //DEBUG
		if(current_string.empty())
		{
			cout<<endl;
			continue;
		}
		if (current_string[0]=='#') 
		{
			cout << current_string << endl;
			continue;
		}
		if (current_string[0]=='>')
		{
			seq_id=current_string;
			in_fasta_block=true;
			continue;
		}
		if (in_fasta_block)
		{
			if (bases_per_error)
				for (size_t pos=0;pos<=current_string.length();pos++)
					if (!dist_error_prob(gen)) //error prob
					{
						current_string[pos]=atgc[error_base(gen)];
						seq_id=seq_id+"%"+boost::lexical_cast<string>(pos);
					}
			cout << seq_id <<endl<<current_string << endl;
			in_fasta_block=false;
			continue;
		}
		if (current_string[0]=='@') //fastq
		{
			seq_id=current_string;
			seq_id[0]='>';
			in_fastq_block=true;
			in_block_counter=1;
			continue;
		}
		if (in_fastq_block && in_block_counter==1)
		{
			if (bases_per_error)
				for (size_t pos=0;pos<=current_string.length();pos++)
					if (!dist_error_prob(gen)) //error prob
					{
						current_string[pos]=atgc[error_base(gen)];
						seq_id=seq_id+"%"+boost::lexical_cast<string>(pos);
					}
			in_block_counter=2;
			cout << seq_id <<endl<<current_string << endl;
			continue;
		}
		
		if (in_fastq_block && in_block_counter==2)
		{
			in_block_counter=3;
			continue;
		}

		if (in_fastq_block && in_block_counter==3)
		{
			in_fastq_block=false;
			in_block_counter=0;
			continue;
		}
		cerr<<"ERROR!!!"<<endl;
		return 1;
	}


}
