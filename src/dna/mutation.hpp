/****************************************************************************\
mutation-call-by-coverage
$Id$
\****************************************************************************/

#ifndef _MUTATION_HPP
#define _MUTATION_HPP

#include <vector>
#include <string>
#include <iterator>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <math.h>

#include "Exception.hpp"
#include "Atgc.hpp"
//The sequence is a set unsigned shorts in range 1..letters_in_alphabet.
//It is capped with \0 at the end.
//

#define usort unsigned short

extern "C"
{
	#include "Random.h"
}
//we suppose that the random generator is already seede

struct mutation{
	mutation():chr(""),copy(0),pos(0),wild(0),mutated(0){};
	mutation(string chr,unsigned long pos,ushort copy,unsigned short wild,unsigned short mutated=0):
		chr(chr),copy(copy),pos(pos),wild(wild),mutated(mutated)
		{
			if (!mutated) mutate();
		}
	mutation(string chr,unsigned long pos,ushort copy,char wild,char mutated='x') throw (AtgcException):
		chr(chr),copy(copy),pos(pos),wild(Atgc::atgc2ushort(wild)),mutated(Atgc::atgc2ushort(mutated))
		{
			if (!mutated) mutate();
		};
	string chr;
	unsigned short copy; // 0 is 'unknown'
	unsigned long pos;
	unsigned short wild;
	unsigned short mutated;
	void choose_copy()
	{
		copy=(int)(floorf(2.*uni()))+1; //1,2
	}
	void mutate()
	{
		unsigned int delta=(int)(floorf(3.*uni()))+1; //1,2,3
		mutated=1+(wild+delta-1)%4;
	}
	bool operator< (const mutation &mu) const
	{
		return (pos<mu.pos);
	}
};


inline
std::ostream& operator<<(std::ostream & os, const mutation & mu) throw (AtgcException)
{
	os<<mu.chr<<":"<<mu.copy<<":"<<mu.pos<<":"<<Atgc::ushort2atgc(mu.wild)<<":"<<Atgc::ushort2atgc(mu.mutated);
	return os;
}

inline
std::istream & operator>> (std::istream & is, mutation & mu) 
												throw (AtgcException, IOStreamException)
{
	string s;
	bool eof=false;
	while( !s.length() && !(eof=is.eof())) is>>s;
	if (eof)
	{
		throw	* new IOStreamException("Read mutation from eof!\n");
	}
	string sep = ":";
	size_t current;
	size_t next = -1;
	vector<string> tokens;
	do
	{
		current = next + 1;
		next = s.find_first_of(sep,current);
		tokens.push_back(s.substr( current, next - current ));
	}
	while (next != string::npos);
	if (tokens.size()!=5)
	{
		throw	* new IOStreamException("Read mutation from non-mutation line!\n");
	}
	//copy (tokens.begin(), tokens.end(), std::ostream_iterator<string>(cout, "\n"));
	mu.chr=tokens[0];
	istringstream ( tokens[1] ) >> mu.copy;
	istringstream ( tokens[2] ) >> mu.pos;
	mu.wild=Atgc::atgc2ushort(tokens[3][0]);
	mu.mutated=Atgc::atgc2ushort(tokens[4][0]);
	return is;
}

inline 
void apply (const mutation & mu, std::vector<ushort> & dna, unsigned long start=0, ushort copy=0)
	throw (DumbException)
{
#define CHECKS 1
#if CHECKS>0
	if (copy && !(copy == mu.copy ))
		throw	* new DumbException("Applying mutation to a wrong copy!\n");
	if (start>mu.pos)
		throw	* new DumbException("Applying mutation to wrong position!\n");
#endif
	size_t pos=mu.pos-start;
#if CHECKS>0
	if (mu.wild != dna[pos])
		throw	* new DumbException("Applying mutation to a wrong base!\n");
#endif
	dna[pos]=mu.mutated;
}

#endif
