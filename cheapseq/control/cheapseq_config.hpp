/****************************************************************************\
mutation-call-by-coverage
$Id$
\****************************************************************************/

#ifndef COV_MUT_CONFIG_HPP
#define COV_MUT_CONFIG_HPP

#define SEED_1 1248312
#define SEED_2 7436111
#define NSEED_1 2732596
#define NSEED_2 6596412

#include <string>
#include <stdio.h>
#include <iostream>
#include <iomanip>
#include <boost/program_options.hpp>

struct config_parameters
{
	std::string fasta_file;
	std::string chromosome_name;
	unsigned int bases_per_snv;
	unsigned int read_length;	
	unsigned int coverage;
	std::string mutations_file;
	std::string reads_file;
	unsigned int random_seed_1,random_seed_2;
	unsigned int noiser_bases_per_error;
	unsigned int noiser_random_seed_1,noiser_random_seed_2; 
	config_parameters():
		fasta_file(""),
		chromosome_name(""),
		bases_per_snv(1000),
		read_length(100),
		coverage(100),
		mutations_file("mutations"),
		reads_file("reads"),
		random_seed_1(SEED_1),
		random_seed_2(SEED_2),
		noiser_bases_per_error(0),
		noiser_random_seed_1(NSEED_1),
		noiser_random_seed_2(NSEED_2)
		{};


	config_parameters(int ac, char** av) throw (DumbException,IOStreamException):
		fasta_file(""),
		chromosome_name(""),
		bases_per_snv(1000),
		read_length(100),
		coverage(100),
		mutations_file("mutations"),
		reads_file("reads"),
		random_seed_1(SEED_1),
		random_seed_2(SEED_2),
		noiser_bases_per_error(0),
		noiser_random_seed_1(NSEED_1),
		noiser_random_seed_2(NSEED_2)
	{
		boost::program_options::options_description desc
				("Cheapseq options for config file or command line.\n   Command-line options override config file;\n   section.option is the same as option in [section].\n");
		desc.add_options()
				("help", "help")
				("config-file", boost::program_options::value<string>(), "configuration file name")
				("cheapseq.fasta_file", boost::program_options::value<string>(&fasta_file), "input FASTA file")
				("cheapseq.chromosome_name", boost::program_options::value<string>(&chromosome_name), "chromosome name")
				("cheapseq.bases_per_snv", boost::program_options::value<unsigned int>(&bases_per_snv), "one mutation (snv) is exopected per this number of bases")
				("cheapseq.read_length", boost::program_options::value<unsigned int>(&read_length), "length of each read")
				("cheapseq.coverage", boost::program_options::value<unsigned int>(&coverage), "cheap (model) sequencing coverage")
				("cheapseq.reads_file", boost::program_options::value<string>(&reads_file), "output FASTA file with reads")
				("cheapseq.mutations_file", boost::program_options::value<string>(&mutations_file), "output file with mutations that we generated and coded in reads")
				("cheapseq.random_seed_1", boost::program_options::value<unsigned int>(&random_seed_1), "random seed 1 for cheap sequencing")
				("cheapseq.random_seed_2", boost::program_options::value<unsigned int>(&random_seed_2), "random seed 2 for cheap sequencing")
				("noiser.bases_per_error", boost::program_options::value<unsigned int>(&noiser_bases_per_error), "one noise error is expected per this number of bases\n\t\t\tdefaut is 0 (no noise)")
				("noiser.random_seed_1", boost::program_options::value<unsigned int>(&noiser_random_seed_1), "random seed 1 for noiser")
				("noiser.random_seed_2", boost::program_options::value<unsigned int>(&noiser_random_seed_2), "random seed 2 for noiser")
		;

	//	boost::program_options::options_description desc("My options");

		try { 
			boost::program_options::positional_options_description pd; 
			pd.add("config-file", -1);
			boost::program_options::variables_map vm;
			boost::program_options::store(boost::program_options::command_line_parser(ac, av).options(desc).positional(pd).run(), vm);

			boost::program_options::notify(vm);

			if (vm.count("help")) {
					cout << desc << "\n";
					throw (*new DumbException(""));
			}

			if (vm.count("config-file")) 
			{
				ifstream conf(vm["config-file"].as<string>().c_str());
				if (!conf) throw (*new IOStreamException("File cannot be opened for read.\n"));
				boost::program_options::store(boost::program_options::parse_config_file(conf, desc, true), vm);
			}

			boost::program_options::notify(vm);
		
		} catch( const exception& e)
			{
					throw (*new DumbException(e.what()));
			}
	}
};

inline
ostream & operator<< (ostream & os, const config_parameters & cp) 
{
	os<<"[cheapseq]"<<endl;
	os<<"fasta_file"<<"="<<cp.fasta_file<<endl;
	os<<"chromosome_name"<<"="<<cp.chromosome_name<<endl;
	os<<"bases_per_snv"<<"="<<cp.bases_per_snv<<endl;
	os<<"read_length"<<"="<<cp.read_length<<endl;
	os<<"coverage"<<"="<<cp.coverage<<endl;
	os<<"mutations"<<"="<<cp.mutations_file<<endl;
	os<<"reads"<<"="<<cp.reads_file<<endl;
	os<<"random_seed_1"<<"="<<cp.random_seed_1<<endl;
	os<<"random_seed_2"<<"="<<cp.random_seed_2<<endl;
	if (cp.noiser_bases_per_error) //>0
	{
		os<<"[noiser]"<<endl;
		os<<"bases_per_error="<<cp.noiser_bases_per_error<<endl;
		os<<"random_seed_1"<<"="<<cp.noiser_random_seed_1<<endl;
		os<<"random_seed_2"<<"="<<cp.noiser_random_seed_2<<endl;
	}
	return os;
}


#endif
