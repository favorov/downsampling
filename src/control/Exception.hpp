/****************************************************************************\
mutation-call-by-coverage
$Id: Exception.hpp 1014 2009-03-01 16:50:36Z favorov $
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
