/*****************************************************************************\
mutation-call-by-coverage
$Id$
\*****************************************************************************/

#ifndef _ATGC_HPP
#define _ATGC_HPP

//#include <ctype.h>

#include <iostream>
#include <iomanip>

#include <vector>
#include <string>

#include <stdio.h>
#include <math.h>

using namespace std;

#include "Exception.hpp"

//Here, we define unsigned short <-> atgc letter functions and
//procedure to output unsigned short * array faragment as 
//atgc sequence fragment.
//
//We do not define a definite class line 
//AtgcVector::public vector<unsigned short> for we are not sure what it need

const unsigned short MaxAtgcSymbol = 5;

const char atgc[6]={'x','a','t','g','c','n'};

//s = g || c (strong)
//w = a || t (weak)

//r = a || g (purines)
//y = c || t (pyrimidines)

//k = g || t
//m = a || c

//b = g || t || c (no - a)
//h = a || t || c (no - g)

//n = any residue, now the only used.
// a set of 1,2,3,4 correspods to a,t,g,c 

class Atgc
{
public:
	static char ushort2atgc(unsigned short symbol) throw (AtgcException);
	static unsigned short atgc2ushort(char letter) throw (AtgcException);
	static unsigned short complement(unsigned short sym);
	static char complement(char sym);

	static vector<unsigned short> & complement
			(
				 const vector<unsigned short> & source, 
				 vector<unsigned short> & dest
			); 

	static vector<unsigned short> & complement
			(
				 vector<unsigned short> & source 
			);  //in-place version

	static string & complement
			(
				 const string & source, 
				 string & dest
			); 

	static string & complement
			(
				 string & dest 
			);  //in-place version

	static string & ushortv2string
			(
				 const vector<unsigned short> & source, 
				 string & dest=*new(string)
			)	throw (AtgcException);

	static vector<unsigned short> & string2ushortv 
			(
				 const string & source, 
				 vector<unsigned short> & dest=*new (vector<unsigned short>)
			) throw (AtgcException);

};

inline
unsigned short Atgc::atgc2ushort(char letter) throw (AtgcException)
{
	char a=tolower(letter);
	if (a=='a') return 1;
	if (a=='t') return 2;
	if (a=='g') return 3;
	if (a=='c') return 4;
	//we suppose that the random generator is already inited.
	if (a=='n') return 5; 
	if (a=='x') return 0;
	string message="Trying to read symbol \'";
	message+=letter;
	message+="\' as nucleoutide.\n";
	throw * new AtgcException(message.c_str());
	return 0;
}

inline
char Atgc::ushort2atgc(unsigned short symbol) throw (AtgcException)
{
	if (symbol>MaxAtgcSymbol)
	{
		string message="Trying to interpret ";
		char symb_no[10];
	  snprintf(symb_no,9,"%1i", symbol);	
		message+=symb_no;
		message+=" as an atgc number (1..4).\n";
		throw * new AtgcException("Trying to get atgc char from something other then 1..4.\n");
	}
	return atgc[symbol];
}

inline
unsigned short Atgc::complement(unsigned short sym)
{
//	1<->2
//	3<->4
		return sym+(sym%2)*2-1;
}

inline
char Atgc::complement(char sym)
{
	unsigned short up=isupper(sym);
	char a=tolower(sym);
	if (a=='a') return up?toupper('t'):'t';
	if (a=='t') return up?toupper('a'):'a';
	if (a=='g') return up?toupper('c'):'c';
	if (a=='c') return up?toupper('g'):'g';
	if (a=='n') return up?toupper('n'):'n'; 
	if (a=='w') return up?toupper('w'):'w';
	if (a=='s') return up?toupper('s'):'s';
	if (a=='r') return up?toupper('y'):'y';
	if (a=='y') return up?toupper('r'):'r';
	string message="Trying to fing complement to symbol \'";
	message+=sym;
	message+="\'.\n";
	throw * new AtgcException(message.c_str());
	return 0;
}

inline
vector<unsigned short> & Atgc::complement
		(
			 vector<unsigned short> & dest
		)
{
	//we do not use STL swap because it is more quick to swap and 
	//reverse bases in one pass.
	//on the other hand, we want the algoryth to be stable for in-place
	//operations. the part is not time_critical.
	vector<unsigned short>::iterator l=dest.begin();
	vector<unsigned short>::iterator r=dest.end();
	r--;
	while (l<=r)
	{
		unsigned short buf=*l;
		*l++=complement(*r);
		*r--=complement(buf);
	}
	return dest;
}

inline
vector<unsigned short> & Atgc::complement
		(
			 const vector<unsigned short> & source, 
			 vector<unsigned short> & dest
		)
{
	//we do not use STL swap because it is more quick to swap and 
	//reverse bases in one pass.
	//on the other hand, we want the algoryth to be stable for in-place
	//operations. the part is not time_critical.
	if (&source==&dest) return complement(dest);
	dest.clear();
	vector<unsigned short>::const_iterator r=source.end();
	r--;
	while (source.begin()<=r)
		dest.push_back(complement(*r--));
	return dest;
}

inline
string & Atgc::complement
			(
				 string & dest 
			)  //in-place version
{
	//we do not use STL swap because it is more quick to swap and 
	//reverse bases in one pass.
	//on the other hand, we want the algoryth to be stable for in-place
	//operations. the part is not time_critical.
	string::iterator l=dest.begin();
	string::iterator r=dest.end();
	r--;
	while (l<=r)
	{
		char buf=*l;
		*l++=complement(*r);
		*r--=complement(buf);
	}
	return dest;
}

inline
string & Atgc::complement
			(
				 const string & source, 
				 string & dest
			) 
{
	//we do not use STL swap because it is more quick to swap and 
	//reverse bases in one pass.
	//on the other hand, we want the algoryth to be stable for in-place
	//operations. the part is not time_critical.
	if (&source==&dest) return complement(dest);
	dest.erase();
	string::const_iterator r=source.end();
	r--;
	while (source.begin()<=r)
		dest.push_back(complement(*r--));
	return dest;
}


inline
string & Atgc::ushortv2string
(
	 const vector<unsigned short> & source, 
	 string & dest
)	throw (AtgcException)
{
	dest="";
	vector<unsigned short>::const_iterator r=source.begin();
	while ( r!=source.end() )
		dest.push_back(ushort2atgc(*r++));
	return dest;
}

inline
vector<unsigned short> & Atgc::string2ushortv 
			(
				 const string & source, 
				 vector<unsigned short> & dest
			) throw (AtgcException)
{
	dest.clear();
	string::const_iterator r=source.begin();
	while ( r!=source.end() )
		dest.push_back(atgc2ushort(*r++));
	return dest;
}

#endif // _ATGC_HPP
