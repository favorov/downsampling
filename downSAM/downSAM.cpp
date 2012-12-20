/****************************************************************************\
mutation-call-by-coverage
$Id: noiser.cpp 1778 2012-07-11 16:41:02Z favorov $
\****************************************************************************/
#include <string>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <iterator>
#include <vector>
#include <algorithm>
#include <boost/program_options.hpp>
#include <boost/random/ranlux.hpp>
#include <boost/random/uniform_int_distribution.hpp>
#include <boost/random/seed_seq.hpp>
#include <boost/lexical_cast.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/regex.hpp>

#define DSEED_1 6506694
#define DSEED_2 6579589

boost::random::ranlux64_4 gen;
//generator is to be the only

using namespace std;

int main(int argc, char ** argv)
{
	unsigned int one_from_reads;
	unsigned int min_read_length;
	unsigned int random_seed_1;
	unsigned int random_seed_2;
	string sample_id_postfix;
	string random_state_file;
	boost::program_options::options_description desc
			("downSAM: reads SAM, outputs SAM.\n Detects reads by mean_read_length length sunstring of [ATGCatgc].\n Output only part of them, on random. All other line are outputed as-is. \n Command-line options override config file;\n   section.option is the same as option in [section].\n Options (config file lines)");
	desc.add_options()
			("help", "help")
			("config-file", boost::program_options::value<string>(), "configuration file name")
			("downSAM.one_from_reads", boost::program_options::value<unsigned int>(&one_from_reads)->default_value(1), "how much input reads are expected per one output")
			("downSAM.min_read_length", boost::program_options::value<unsigned int>(&min_read_length)->default_value(30), "minimal length of read, to detect reads by [ATGCatgc]{min_read_length} regex")
			("downSAM.random_seed_1", boost::program_options::value<unsigned int>(&random_seed_1)->default_value(DSEED_1), "random seed 1 for noiser")
			("downSAM.random_seed_2", boost::program_options::value<unsigned int>(&random_seed_2)->default_value(DSEED_2), "random seed 2 for noiser")
			("downSAM.sample_id_postfix", boost::program_options::value<string>(&sample_id_postfix), "the posfix to be added to both SM and ID fields of @RG line")
			("downSAM.random_state_file", boost::program_options::value<string>(&random_state_file), "random generator state file;\nthe state is read from the file on start\nand it is saved to the file on finish;\nif the option is given and the file exists,\nthe random_seed options are not used")
	;
	try { 
		boost::program_options::positional_options_description pd; 
		pd.add("config-file", -1);
		boost::program_options::variables_map vm;
		boost::program_options::store(boost::program_options::command_line_parser(argc, argv).options(desc).positional(pd).run(), vm);

		//boost::program_options::notify(vm);

		if (vm.count("help")) {
			cerr << desc << "\n";
			return 0;
		}

		if (vm.count("config-file")) 
		{
			ifstream conf(vm["config-file"].as<string>().c_str());
			if (!conf)
			{
				cerr<<"File \""<<vm["config-file"].as<string>().c_str()<<"\" cannot be opened for read.\n";
				return 1;
			}
			boost::program_options::store(boost::program_options::parse_config_file(conf, desc, true), vm);
		}

		boost::program_options::notify(vm);
	
	} catch( const exception& e)
	{
			cerr<<e.what()<<endl<<desc<<endl;
	}

	bool to_seed=true;

	if (random_state_file!="")
	{
		ifstream gen_init_load(random_state_file.c_str());
		if (gen_init_load.good()) 
		{
			gen_init_load>>gen;
			gen_init_load.close();
			to_seed=false;
		}
	}
	if (to_seed)
	{
		std::vector<unsigned long> iniseed(2);
		iniseed[0]=random_seed_1;
		iniseed[1]=random_seed_2;
		boost::random::seed_seq iniseedseq(iniseed);
		gen.seed(iniseedseq);
	}

	boost::random::uniform_int_distribution<unsigned int> to_write_or_not_to_write(0,one_from_reads-1);
	string current_string;
	
	string read_regex_string="^.+[ATGCatgc]{"+boost::lexical_cast<string>(min_read_length)+",}.+$";
	string PG_regex_string="^@PG.*$";
	string RG_regex_string="^@RG.*$";
	string ID_regex_string="^ID:.*$";
	string SM_regex_string="^SM:.*$";
	
	boost::regex read_signat(read_regex_string);
	boost::regex PG_signat(PG_regex_string);
	boost::regex RG_signat(RG_regex_string);
	boost::regex ID_signat(ID_regex_string);
	boost::regex SM_signat(SM_regex_string);
	
	bool PG_written=false,PG_writing=false,HEAD_over=false;
	//cerr<<read_regex_string<<endl;
	

	while (!cin.eof())
	{
		getline(cin, current_string);
		boost::trim(current_string);
		if (!HEAD_over)	//we are in header
		{	
			if (!PG_written)
			{
				//we care about @PG only once
				if( boost::regex_match(current_string, PG_signat))
				{
					cout<<current_string<<endl;
					PG_writing=true;
					//we started @PG output
					continue;
				}
				else
				{
					if(PG_writing) //so, the PG module is finished right now
					{
						cout<<"@PG\tID:downSAM\tVN:1.0.1\tCL:\"downSAM --downSAM.one_from_reads "<<one_from_reads<<" --downSAM.min_read_length "<<min_read_length<<"\""<<endl; //wrote our @PG signature
						PG_writing=false;
						PG_written=true;
						//we finished @PG output, the string we read goes further
					}
					//else, we do nothing: it is not @PG-related situation, if it does not match read_signat, it will be printed later
				}
			}

			if( boost::regex_match(current_string, RG_signat))
			{
				istringstream stream(current_string);
				vector<string> RG_tokens;
				copy(istream_iterator<string>(stream),
								 istream_iterator<string>(),
								 back_inserter<vector<string> >(RG_tokens));
				for (vector<string>::iterator token=RG_tokens.begin();token<RG_tokens.end();token++)
				{
					if( boost::regex_match(*token, ID_signat))
						*token+=sample_id_postfix;
					if( boost::regex_match(*token, SM_signat))
						*token+=sample_id_postfix;
					if (token+1<RG_tokens.end())
						cout<<*token<<"\t";
					else
						cout<<*token<<endl;
				}
				continue;
			}
			
			if( boost::regex_match(current_string, read_signat))
			//read
			{
				HEAD_over=true; //it is a read, goodbye, header
				if (!PG_written)
				{
					cout<<"@PG\tID:downSAM\tVN:1.0.1\tCL:\"downSAM --downSAM.one_from_reads "<<one_from_reads<<" --downSAM.min_read_length "<<min_read_length<<"\""<<endl; //wrote our @PG signature
					PG_written=true; //  actually, we do need it
				}
				if (! to_write_or_not_to_write(gen))
					cout<<current_string<<endl;
				continue;
			}

			cout<<current_string<<endl; //it is a header string, no idea what
		}
		else // header is over; we think that every line is a read
			if (! to_write_or_not_to_write(gen))
				cout<<current_string<<endl;
	}

	if (random_state_file!="")
	{
		ofstream gen_init_save(random_state_file.c_str());
		if (!gen_init_save.good()) {cerr<<"Cannot open random generator state file for write.\n";}
		gen_init_save<<gen;
		gen_init_save.close();
	}

}
