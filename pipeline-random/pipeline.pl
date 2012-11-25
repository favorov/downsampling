#!/usr/bin/perl -w 
#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
use strict;

my $cheapseq_folder="../coverage/cheapseq"


my $argc = @ARGV;

print "\ncovearage.pl runs the coverage-testing pipeline .\n
Usage: perl coverage config-file\n" and exit if ($argc!=1); 

print "\ncovearage.pl runs the coverage-testing pipeline on a config file.\n
Usage: perl report2vcf config-file\n
First, it tests whether the Fasta with reads exist 
If no, it runs cheapseq config-file 
If mutations file is newer that its vcf form or the latter does not exist, rewrite vcf

\n\n
" and exit if 
(
	$argc==1 and 
		(
			$ARGV[0] eq '--help'
			||
			$ARGV[0] eq '--h'
			||
			$ARGV[0] eq '-h'
			||
			$ARGV[0] eq '-help'
		)
);

open( CONFIG, $ARGV[0] ) or print "Can't open config file $ARGV[0]. Error is  '$!' \n" and exit;

my ($fasta_file, $sample_id, $mutations_file);

while (<CONFIG>) {
	chomp;
	s/\r//g;
	next if /^#/;
	my @line = split("=");
	$line[0] = "" if not defined $line[0];
	$line[1] = "" if not defined $line[1];

	#	print "\'$line[0]\' = \'$line[1]\'\n";
	$fasta_file     				= $line[1] if $line[0] eq 'fasta_file';
	$sample_id     				= $line[1] if $line[0] eq 'sample_id';
	$mutations_file = $line[1] if $line[0] eq 'mutations_file';
}


