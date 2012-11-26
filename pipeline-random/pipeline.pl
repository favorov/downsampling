#!/usr/bin/perl -w 
#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
use strict;

my $cheapseq_folder="../cheapseq";
my $report2vcf_folder=$cheapseq_folder;


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

my $cfile_name=$ARGV[0];

open( CONFIG, $cfile_name ) or print "Can't open config file $cfile_name. Error is  '$!' \n" and exit;

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

print "#Random coverage mutatition test pipeline. Config file is $ARGV[0], sample id is $sample_id.";

if (! -e $mutations_file) 
{
	my $cheapseq_string=$cheapseq_folder."/cheapseq";
	print "#Start cheapseq...\n";
	system($cheapseq_string,$cfile_name) == 0 or die ("Cheapseq start failed: $?\n");
	print "#Finished (cheapseq) ...\n";
}
