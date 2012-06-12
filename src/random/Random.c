//$Id$
//
#include <math.h>

//The name "ultra is for the memory of fsultra library - the base of this code
//
//Changes: the initilizer has got two lines 
//  ij=ij%31328;
//	kl=kl%30081;
//	which allow to use it with any start numbers.
//	array returned by rnmar() in now 0-based.
//
//  added ultra-like 
//  void rinit(long,long) and
//  float uni()
//
//	21.09.2000. A.Favorov.
//

/*
C This random number generator originally appeared in "Toward a Universal
C Random Number Generator" by George Marsaglia and Arif Zaman.
C Florida State University Report: FSU-SCRI-87-50 (1987)
C
C It was later modified by F. James and published in "A Review of Pseudo-
C random Number Generators"
C
C THIS IS THE BEST KNOWN RANDOM NUMBER GENERATOR AVAILABLE.
C       (However, a newly discovered technique can yield
C         a period of 10^600. But that is still in the development stage.)
C
C It passes ALL of the tests for random number generators and has a period
C   of 2^144, is completely portable (gives bit identical results on all
C   machines with at least 24-bit mantissas in the floating point
C   representation).
C
C The algorithm is a combination of a Fibonacci sequence (with lags of 97
C   and 33, and operation "subtraction plus one, modulo one") and an
C   "arithmetic sequence" (using subtraction).
C========================================================================
This C language version was written by Jim Butler, and was based on a
FORTRAN program posted by David LaSalle of Florida State University.
*/

#include <stdio.h>
#include <stdlib.h>

#include "Random.h"

#define TRUE 1
#define FALSE 0
#define boolean int

static float u[98], c, cd, cm;
static int i97, j97;
static boolean test = FALSE;

void rmarin(ij,kl)
int ij, kl;
{
/*
C This is the initialization routine for the random number generator RANMAR()
C NOTE: The seed variables can have values between:    0 <= IJ <= 31328
C                                                      0 <= KL <= 30081
C The random number sequences created by these two seeds are of sufficient
C length to complete an entire calculation with. For example, if sveral
C different groups are working on different parts of the same calculation,
C each group could be assigned its own IJ seed. This would leave each group
C with 30000 choices for the second seed. That is to say, this random
C number generator can create 900 million different subsequences -- with
C each subsequence having a length of approximately 10^30.
C
C Use IJ = 1802 & KL = 9373 to test the random number generator. The
C subroutine RANMAR should be used to generate 20000 random numbers.
C Then display the next six random numbers generated multiplied by 4096*4096
C If the random number generator is working properly, the random numbers
C should be:
C           6533892.0  14220222.0  7275067.0
C           6172232.0  8354498.0   10633180.0
*/
	int i, j, k, l, ii, jj, m;
	float s, t;
	ij=ij%31328;
	kl=kl%30081;
	if (ij<0 || ij>31328 || kl<0 || kl>30081) 
	{
		puts("The first random number seed must have a value between 0 and 31328.");
		puts("The second seed must have a value between 0 and 30081.");
		exit(1);
	}

	i = (ij/177)%177 + 2;
	j = ij%177 + 2;
	k = (kl/169)%178 + 1;
	l = kl%169;

	for (ii=1; ii<=97; ii++) 
	{
		s = 0.0;
		t = 0.5;
		for (jj=1; jj<=24; jj++) 
		{
			m = (((i*j)%179)*k) % 179;
			i = j;
			j = k;
			k = m;
			l = (53*l + 1) % 169;
			if ((l*m)%64 >= 32) s += t;
			t *= 0.5;
		}
		u[ii] = s;
	}

	c = 362436.0 / 16777216.0;
	cd = 7654321.0 / 16777216.0;
	cm = 16777213.0 / 16777216.0;

	i97 = 97;
	j97 = 33;

	test = TRUE;
}

void ranmar(rvec, len)
float rvec[]; /* len random numbers are placed in rvec[0..len-1] */
int len;
/*
C This is the random number generator proposed by George Marsaglia in
C Florida State University Report: FSU-SCRI-87-50
C It was slightly modified by F. James to produce an array of pseudorandom
C numbers.
*/
{
	int ivec;
	float uni;

	if (test==FALSE) 
	{
		puts("Call the init routine rmarin() before calling ranmar().");
		exit(2);
	}
	for (ivec=0; ivec<len; ivec++) 
	{
		uni = u[i97] - u[j97];
		if (uni < 0.0) uni += 1.0;
		u[i97] = uni;
		i97--;
		if (i97==0) i97 = 97;
		j97--;
		if (j97==0) j97 = 97;
		c -= cd;
		if (c<0.0) c += cm;
		uni -= c;
		if (uni<0.0) uni += 1.0;
		rvec[ivec] = uni;
	}
} 

void rinit(unsigned long seed1,unsigned long seed2)
{
	int ij,kl;
	ij=seed1%31328;
	kl=seed2%30081;
	rmarin(ij,kl);
}

float uni()
{
	float f;
	ranmar(&f,1);
	return f;
}
//these two interfaces are added by A. Favorov to 
//maintain ultra-based code.

/*+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 * Function:  Rangauss
 * 
 * Purpose:   Sample from Gaussian N(0,1)
 * 
 * Notes: (1) Requires previous call to RanInit to initialise the generator
 *            stored in Rand[0..111] AND the Rangauss switch in Rand[112]
 *        (2) Maximum outlier extent cannot quite reach 7 standard deviations
 *        (3) Generates 2 deviates every other call
 * 
 * History:   JS         22 Jan 1994   Box-Muller
 *                       19 Oct 1995
 *-----------------------------------------------------------------------------
 */

