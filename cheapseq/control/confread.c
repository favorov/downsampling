/***************************************************************\
  APSampler. Looking for complex genetic interaction patterns
 by a Metropolis-Hastings MCMC project. (c) A. Favorov 1999-2010
    $Id$
\***************************************************************/

#include <assert.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include "confread.h"

//1 - OK
//0 - do not find. (mute)
//-5 - the tag is but it is not of the desired type
//-10 - file format error
//-100 - file open eror

int ReadConfigString(FILE *ifile, const char *tag,
		char *value, unsigned int allocated_value_len,is_obligatory_type is_obligatory)
{
	char *buf;
	char *string;
	char *src,*token;
	buf=(char*)calloc(Conf_File_Line_Len+1,sizeof(char));
	assert(buf);
	if (!ifile)
	{
		fprintf(stderr,"NULL file to read %s from\n",tag);
		return -100;
	}
	fseek(ifile, 0, SEEK_SET);
	while (fgets(buf,Conf_File_Line_Len+1,ifile))//Main cycle
	{
		if (strchr(buf,'\0')==buf+Conf_File_Line_Len)
		{
			fprintf(stderr,"A config file line is longer than %i that is built-in max length. The line is:\n%s\n",Conf_File_Line_Len,buf);
			exit (-231);	
		}
		src=buf+strlen(buf)-1; //end of buffer
		*src=(*src=='\n')?'\0':*src; //to fgets()'s trailing endline
		*src=(*src=='\r')?'\0':*src;
		src--;
		*src=(*src=='\n')?'\0':*src;
		*src=(*src=='\r')?'\0':*src; //removing any kind of endline
		buf[Conf_File_Line_Len]='\0'; //na vsiakij sluchaj
		if(*buf=='\0') continue;//empty line

		src = strchr(buf,'#');
		if (src) *src='\0';  //we has removed comment if found

		src = buf+strspn(buf," \t"); //remove starting spaces and tabs
		if (*src=='\0') continue;//empty line
		token = strchr(src,'=');
		if (!token)
		{
			fprintf(stderr,"Cannot parse a line in config file for it has no \'=\':\n%s\n.\n",buf);
			return -10;
		}
		*(token++)='\0';
		token = token+strspn(token," \t"); //remove starting spaces and tabs
		string=token; //we've remebered symbols after =
		token=strtok(src," \t");
		if (!token)
		{
			fprintf(stderr,"Empty tag line in config file\n");
			return -10;
		}
		if (strcmp(token,tag)) continue; //we do need this line
		strncpy(value,string,allocated_value_len-1);
		value[allocated_value_len-1]='\0';
		return 1;
	}
	if (is_obligatory==obligatory) fprintf (stderr,"Cannot find tag %s in config file.\n",tag);
	free(buf);
	return 0; //ne nashli
}

int ReadConfigBoolean(FILE *ifile, const char *tag,unsigned int *value,is_obligatory_type is_obligatory)
{
	char *str_value;
	int read_result;
	str_value=(char*)calloc(Boolean_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																Boolean_String_Len+1,is_obligatory);
	if (read_result<=0)
	{
		free(str_value);
		return read_result;
	}
	*value=2; //nonsense nalue
	if (!strncmp(str_value,"true",Boolean_String_Len+1))*value=1;
	if (!strncmp(str_value,"yes",Boolean_String_Len+1))*value=1;
	if (!strncmp(str_value,"on",Boolean_String_Len+1))*value=1;
	if (!strncmp(str_value,"1",Boolean_String_Len+1))*value=1;
	if (!strncmp(str_value,"false",Boolean_String_Len+1))*value=0;
	if (!strncmp(str_value,"no",Boolean_String_Len+1))*value=0;
	if (!strncmp(str_value,"off",Boolean_String_Len+1))*value=0;
	if (!strncmp(str_value,"0",Boolean_String_Len+1))*value=0;
	free(str_value);
	if (*value==2)
	{
		fprintf(stderr,"Tag %s is not Boolean.\n",tag);
		return -5;
	}
	return 1;
}

int ReadConfigInt(FILE *ifile, const char *tag, int *value,is_obligatory_type is_obligatory)
{
	char *str_value;
	int read_result;
	char * ptr;
	str_value=(char*)calloc(Int_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																Int_String_Len+1,is_obligatory);
	if (read_result<=0)
	{
		free(str_value);
		return read_result;
	}
	*value=strtol(str_value,& ptr,0);
	if (ptr!=(str_value+strlen(str_value)) )
	{
		fprintf(stderr,"Tag %s is not integer.\n",tag);
		free(str_value);
		return -5;
	}
	free(str_value);
	return 1;
}

int ReadConfigLong(FILE *ifile, const char *tag, long *value,is_obligatory_type is_obligatory)
{
	char *str_value;
	int read_result;
	char * ptr;
	str_value=(char*)calloc(Int_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																Int_String_Len+1,is_obligatory);
	if (read_result<=0)
	{
		free(str_value);
		return read_result;
	}
	*value=strtol(str_value,& ptr,0);
	if (ptr!=(str_value+strlen(str_value)) )
	{
		fprintf(stderr,"Tag %s is not integer.\n",tag);
		free(str_value);
		return -5;
	}
	free(str_value);
	return 1;
}

int ReadConfigUnsignedLong(FILE *ifile, const char *tag, unsigned long *value,
		is_obligatory_type is_obligatory)
{
	char *str_value;
	int read_result;
	char * ptr;
	str_value=(char*)calloc(Int_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																Int_String_Len+1,is_obligatory);
	if (read_result<=0)
	{
		free(str_value);
		return read_result;
	}
	*value=strtoul(str_value,& ptr,0);
	if (ptr!=(str_value+strlen(str_value)) )
	{
		fprintf(stderr,"Tag %s is not integer.\n",tag);
		free(str_value);
		return -5;
	}
	free(str_value);
	return 1;
}

int ReadConfigUnsignedInt(FILE *ifile, const char *tag, unsigned int *value,
		is_obligatory_type is_obligatory)
{
	char *str_value;
	int read_result;
	char * ptr;
	str_value=(char*)calloc(Int_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																Int_String_Len+1,is_obligatory);
	if (read_result<=0)
	{
		free(str_value);
		return read_result;
	}
	*value=strtoul(str_value,& ptr,0);
	if (ptr!=(str_value+strlen(str_value)) )
	{
		fprintf(stderr,"Tag %s is not integer.\n",tag);
		free(str_value);
		return -5;
	}
	free(str_value);
	return 1;
}


int ReadConfigDouble(FILE *ifile, const char *tag, double *value,is_obligatory_type is_obligatory)
{
	char *str_value;
	int read_result;
	char * ptr;
	str_value=(char*)calloc(Int_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																Int_String_Len+1,is_obligatory);
	if (read_result<=0)
	{
		free(str_value);
		return read_result;
	}
	*value=strtod(str_value,& ptr);
	if (ptr!=(str_value+strlen(str_value)) )
	{
		fprintf(stderr,"Tag %s is not double.\n",tag);
		free(str_value);
		return -5;
	}
	free(str_value);
	return 1;
}

int ReadConfigIntList(FILE *ifile, const char *tag, int **list, int* list_lenght,
		is_obligatory_type is_obligatory)
//it allocates the list and returns its length in list_lenght.
{
	char *str_value,*token;
	int read_result;
	char * ptr;
	int * list_value;
	int read=0;

	str_value=(char*)calloc(List_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																List_String_Len+1,is_obligatory);
	list_value=(int*)calloc(Max_Int_List_Len,sizeof(int));
	assert(list_value);
	if (read_result<=0)
	{
		free(str_value);
		free(list_value);
		return read_result;
	}
	while( (token=strtok(read?NULL:str_value,";:,")) )
	{
		list_value[read]=strtol(token,& ptr,0);
		if (ptr!=(token+strlen(token)) )
		{
			free(str_value);
			free(list_value);
			fprintf(stderr,"Tag %s is not an integer list (element %i).\n",tag,read);
			return -5;
		}
		read++;
	}
	*list=(int*)calloc(read,sizeof(int));
	assert(*list);
	*list_lenght=read;
	for(read=0;read<*list_lenght;read++)
		(*list)[read]=list_value[read];
	free(str_value);
	free(list_value);
	return 1;
}

int ReadConfigRepeatedIntList(FILE *ifile, const char *tag, int_repeat_type **list, int* list_lenght,
		is_obligatory_type is_obligatory)
//it allocates the list and returns its length in list_lenght.
{
	char *str_value,*token;
	int read_result;
	char * ptr;
	int_repeat_type * list_value;
	int read=0;

	str_value=(char*)calloc(List_String_Len+1,sizeof(char));
	assert(str_value);
	read_result=ReadConfigString(ifile,tag,str_value,
																List_String_Len+1,is_obligatory);
	list_value=(int_repeat_type*)calloc(Max_Int_List_Len,sizeof(int_repeat_type));
	assert(list_value);
	if (read_result<=0)
	{
		free(str_value);
		free(list_value);
		return read_result;
	}
	while( (token=strtok(read?NULL:str_value,";:,")) )
	{
		list_value[read].value=strtol(token,& ptr,0);
		if (ptr==(token+strlen(token)) )
			list_value[read].times=1; //no * part
		else if (*ptr=='*')
		{
			token=ptr+1;
			list_value[read].times=strtol(token,& ptr,0);
			if (ptr!=(token+strlen(token)) )
			{
				free(str_value);
				free(list_value);
				fprintf(stderr,"Tag %s is not an integer*repeat list (repeater of element %i).\n",tag,read);
				return -5;
			}
		}
		else
		{
			free(str_value);
			free(list_value);
			fprintf(stderr,"Tag %s is not an integer list (element %i).\n",tag,read);
			return -5;
		}
		read++;
	}
	*list=(int_repeat_type*)calloc(read,sizeof(int_repeat_type));
	assert(*list);
	*list_lenght=read;
	for(read=0;read<*list_lenght;read++)
		(*list)[read]=list_value[read];
	free(str_value);
	free(list_value);
	return 1;
}

