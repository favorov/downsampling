/*****************************************************************************\
mutation-call-by-coverage
$Id$
\*****************************************************************************/

#ifndef _OPEN_GZIP_OR_NOT_GZIP_HPP
#define _OPEN_GZIP_OR_NOT_GZIP_HPP

#include <fstream>
#include <iostream>
#include <string>
#include <boost/iostreams/filtering_streambuf.hpp>
#include <boost/iostreams/copy.hpp>
#include <boost/iostreams/filter/gzip.hpp>

std::istream & open_gzip_or_not_gzip (const std::string & name)
{
	if (!name.substr(length(name)-2,2).compare("gz"))
	{
		std::ifstream file("hello.gz", std::ios_base::in | std::ios_base::binary);
    boost::iostreams::filtering_streambuf<input> in;
    in.push(gzip_decompressor());
    in.push(file);
		std::istream fasta_stream(&in);
		return fasta_stream;
	}
	else
	{
		std::ifstream fasta_fstream(name.c_str());
		return fasta_fstream;
	}
}

#endif

