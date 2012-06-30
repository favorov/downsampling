/****************************************************************************\
mutation-call-by-coverage
$Id$
\****************************************************************************/

#include <stdio.h>
#include <string.h>
//mixed programming, alas....

#include <iostream>
#include <iomanip>
#include <string>

using namespace std;

//it is a version of original Sequences.cpp grom SeSiMCMC
//WITHOUT mask,
//but with CUT - into to make noodle.

#include "Sequences.hpp"
#include "Atgc.hpp"

ostream & operator<< (ostream & os, const SequencesPile & sp) 
												throw (AtgcException) 
{
	for (unsigned int i=0;i<sp.size();i++)
	{
	//write FastA record
		string str;
		Atgc::ushortv2string(sp[i],str);
		os<<">"<<sp.names[i]<<endl<<str;
	//if (fseq.starred) os<<"*";//we use classic FastA with *
		os<<endl;
	}
	return os;
}

istream & operator>> (istream & is, SequencesPile & sp) 
												throw (AtgcException, IOStreamException)
{
//it works with c-style reding. Let it be.
//Structure:
//Name (any string with > in first position)
//Sequence ..... (*-terminated or not)
//Name
//Sequence....
//

	string Buffer;

	string::size_type pos;

	enum  {skipbefore, name_read, name_and_NBRF_comment_read, reading_sequence,
									done} state=skipbefore;

	string sequence_text="", name="", next_name="";

	unsigned short ANameIsReadForNextRecord=0;
	
	vector<unsigned short> ushortv;
	
	while (!is.eof() )
	{

		Buffer.erase();

		getline(is,Buffer,'\n');
		if (Buffer[Buffer.size()-1]=='\015')  //we procced possible trailing '^M'
			Buffer=Buffer.substr(0,Buffer.size()-1);
		if (Buffer[Buffer.size()-1]=='\012')  //we procced possible trailing '^J'
			Buffer=Buffer.substr(0,Buffer.size()-1);
		
		if (Buffer[Buffer.size()-1]=='\015')  //we procced possible trailing '^M'
			Buffer=Buffer.substr(0,Buffer.size()-1);
		if (Buffer[Buffer.size()-1]=='\012')  //we procced possible trailing '^J'
			Buffer=Buffer.substr(0,Buffer.size()-1);
		
		switch(state)
		{
		case skipbefore:
			if (Buffer[0]=='>')
			{
				name=Buffer.substr(1); //we omit the starting ">"
				state=name_read;
				break;
			};
			if (Buffer.find_first_not_of(" \t")!=string::npos)
			throw 
					(
						* new IOStreamException
							("Fasta reader has found nonblank line before name.\n")
					);
			//it can be treat as error or as SequencesPile delimiter
			break;
		case name_read:
		case name_and_NBRF_comment_read:
			//here, we have read the name from previous lines; the line can be 
			//NBRF comment (it has obligatory "-") or
			//empty (omitted) or
			//or the sequence or its part.

			//the NBRF part can appear only once, so:
			if ((pos=Buffer.find_first_not_of(" \t"))!=string::npos)
			{
				if (Buffer[pos]=='-')
				{
					if (state==name_and_NBRF_comment_read)
						throw 
								(
									* new IOStreamException
										("Fasta reader has found two NBRF comments in one record.\n")
								);
					state=name_and_NBRF_comment_read;
					break; //from switch
				}
			}
			else break; //from switch
					


			//if we are here. the line is part of sequence or an error. So,
			//the sequence has been started

		case reading_sequence:
			//now, we are reading a,t,g,c. First, let's reallocate fseq.sequence.
			if (state==reading_sequence) //we came here from switch
																	 //so, it makes sense to test whether 
																	 //the line is empty or is it
																	 //the "> name" title line of next 
																	 //FastA record in stream.
			{
				if (Buffer[0]=='>')
				{
					next_name=Buffer.substr(1);
					ANameIsReadForNextRecord=1;
					state=done;
					break; //from switch
				};
				
				if (Buffer.find_first_not_of(" \t")==string::npos)
				{
					state=done;
					break;
				} //empty string. A sequence is over.
			}
			
			else state=reading_sequence; //we came here from previous case
																	 //because the line was not empty and not 
																	 //NBRF comment

			
			
			if (Buffer[Buffer.size()-1]=='*')  //we procced possible trailing '*'
															           //in FastA, it means end of record
			{
				state=done;
				Buffer=Buffer.substr(0,Buffer.size()-1);
			}
			
			if (is.eof()) state=done; //end of file, nothing more to do
			
			for (
						string::iterator Buf_it=Buffer.begin();
						Buf_it<Buffer.end();
						Buf_it++
					) while (isspace(*Buf_it)) Buffer.erase(Buf_it);
				
			sequence_text.append(Buffer);	
			//iterator
			
		case done: //we never jump here :)
			break;
		
		}
		if (state==done)
		{
			//a record is read
			sp.names.push_back(name);
			sp.push_back(Atgc::string2ushortv(sequence_text,ushortv));
			
			sequence_text="";
			state=skipbefore;
			if (ANameIsReadForNextRecord)
			{
				name=next_name;
				ANameIsReadForNextRecord=0;
				state=name_read;
			}
			//the last "if" works with the situation when there was no delimiter (empty line 
			//or "*" after previous sequence.
			//So, the FastAInputStream object has stored the name started with ""
		}
	}
	return is;
}


