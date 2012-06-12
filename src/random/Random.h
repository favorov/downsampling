//$Id: Random.h 1014 2009-03-01 16:50:36Z favorov $
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
void rmarin(int ij, int kl);
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

void ranmar(float rvec[], int len);
 /*
 C This is the random number generator proposed by George Marsaglia in
 C Florida State University Report: FSU-SCRI-87-50
 C It was slightly modified by F. James to produce an array of pseudorandom
 C numbers.
 */



void rinit(unsigned long seed1,unsigned long seed2);
float uni();
//these two interfaces are added by A. Favorov to 
//maintain ultra-based code.


