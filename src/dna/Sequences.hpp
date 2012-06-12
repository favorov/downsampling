/****************************************************************************\
mutation-call-by-coverage
$Id: Sequences.hpp 1014 2009-03-01 16:50:36Z favorov $
\****************************************************************************/

#ifndef _SEQUENCES_HPP
#define _SEQUENCES_HPP

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#include <vector>
#include <string>
#include <algorithm>
#include <sstream>
//reduced version of original Sequences.hpp grom SeSiMCMC!!!

#include "Exception.hpp"
#include "Atgc.hpp"
//The sequence is a set unsigned shorts in range 1..letters_in_alphabet.
//It is capped with \0 at the end.
//

struct SequencesPile: public std::vector < vector<unsigned short> >
{
	vector <std::string> names;
};


std::ostream & operator<< (std::ostream & os, const SequencesPile & sp) 
												throw (AtgcException); 

std::istream & operator>> (std::istream & is, SequencesPile & sp) 
												throw (AtgcException, IOStreamException); 


#endif // _SEQUENCES_HPP
