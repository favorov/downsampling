/***************************************************************\
mutation-call-by-coverage
$Id: confread.h 1340 2010-11-25 00:42:50Z favorov $
\***************************************************************/

#ifndef _CONFREAD_H_
#define _CONFREAD_H_

#include <stdio.h>

#define Conf_File_Line_Len 2101 //List_String_Len+Tag lenth+1
#define Int_String_Len 10
#define Double_String_Len 30
#define Long_String_len 20
#define Boolean_String_Len 5
#define List_String_Len 2000
#define Max_Int_List_Len 500

typedef enum {optional,obligatory} is_obligatory_type;  

typedef struct {int value; unsigned int times;} int_repeat_type;

int ReadConfigString(FILE *ifile, const char *tag, 
		char *value, unsigned int allocated_value_len,
		is_obligatory_type is_obligatory);
int ReadConfigBoolean(FILE *ifile,const char *tag,unsigned int *value,
		is_obligatory_type is_obligatory);
int ReadConfigInt(FILE *ifile, const char *tag, int *value,
		is_obligatory_type is_obligatory);
int ReadConfigLong(FILE *ifile, const char *tag, long *value,
		is_obligatory_type is_obligatory);
int ReadConfigUnsignedInt(FILE *ifile, const char *tag, unsigned int *value,
		is_obligatory_type is_obligatory);
int ReadConfigUnsignedLong(FILE *ifile, const char *tag, unsigned long *value,
		is_obligatory_type is_obligatory);
int ReadConfigDouble(FILE *ifile, const char *tag, double *value,
		is_obligatory_type is_obligatory);
int ReadConfigIntList(FILE *ifile, const char *tag, int **list, int* list_lenght,
		is_obligatory_type is_obligatory);
int ReadConfigRepeatedIntList(FILE *ifile, const char *tag, int_repeat_type ** list, int* list_lenght,
		is_obligatory_type is_obligatory);

//it allocates the list and returns its length in list_lenght. 

//1 - OK
//0 - do not find. (mute)
//-1 - the tag is but it is not of the desired type (mute)
//-10 - file format error
//-100 - file open eror
#endif // _CONFREAD_H_
   
