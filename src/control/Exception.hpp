/****************************************************************************\
mutation-call-by-coverage
$Id$
\****************************************************************************/

#ifndef _EXCEPTION_HPP
#define _EXCEPTION_HPP

#include <iostream>

using namespace std;

struct DumbException
{
	const char * info;
	DumbException(const char * str=""):info(str){};
};

inline
ostream & operator<< (ostream & o, const DumbException & de)
{
	o<<de.info;
	return o;
}

struct AtgcException : public DumbException
{
	AtgcException(const char * str=""):DumbException(str){};
};

struct IOStreamException : public DumbException
{
	IOStreamException(const char * str=""):DumbException(str){};
};

#endif //_EXCEPTION_HPP
