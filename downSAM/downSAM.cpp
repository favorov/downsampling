/****************************************************************************\
mutation-call-by-coverage
$Id: noiser.cpp 1778 2012-07-11 16:41:02Z favorov $
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
	boost::program_options::options_description desc
			("downSAM: reads SAM, outputs SAM.\n Detects reads by mean_read_length length sunstring of [ATGCatgc].\n Output only part of them, on random. All other line are outputed as-is. \n Command-line options override config file;\n   section.option is the same as option in [section].\n Options (config file lines)");
	desc.add_options()
			("help", "help")
			("config-file", boost::program_options::value<string>(), "configuration file name")
			("downSAM.one_from_reads", boost::program_options::value<unsigned int>(&one_from_reads)->default_value(1), "how much input reads are expected per one output")
			("downSAM.min_read_length", boost::program_options::value<unsigned int>(&min_read_length)->default_value(30), "minimal length of read, to detect reads by [ATGCatgc]{min_read_length} regex")
			("downSAM.random_seed_1", boost::program_options::value<unsigned int>(&random_seed_1)->default_value(DSEED_1), "random seed 1 for noiser")
			("downSAM.random_seed_2", boost::program_options::value<unsigned int>(&random_seed_2)->default_value(DSEED_2), "random seed 2 for noiser")
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

	boost::random::uniform_int_distribution<unsigned int> to_read_or_not_to_read(0,one_from_reads-1);
	string current_string;
	
	string read_regex_string="^.+[ATGCatgc]{"+boost::lexical_cast<string>(min_read_length)+",}.+$";

	//cerr<<read_regex_string<<endl;

	boost::regex read_signat(read_regex_string);
	while (!cin.eof())
	{
		getline(cin, current_string);
		boost::trim(current_string);
		if( boost::regex_match(current_string, read_signat))
		//read
		{
			if (! to_read_or_not_to_read(gen))
				cout<<current_string<<endl;
		}
		else
		//not read
			cout<<current_string<<endl;
	}


}
