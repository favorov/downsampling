#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
#!/usr/bin/perl -w 
use strict;
use vcftools::Vcf;

my $argc = @ARGV;

print "report2vcf.pl converts the mutation report that was genarated by cheapseq to vcf format.\n
Usage: perl report2vcf config-file\n";


open( CONFIG, $ARGV[0] ) or print "Can't open $ARGV[0]: $!\n" and exit;

my ($sample_id,$mutation_file)

while (<CONFIG>) {
	chomp;
	s/\r//g;
	next if /^#/;
	my @line = split("=");
	$line[0] = "" if not defined $line[0];
	$line[1] = "" if not defined $line[1];

	#	print "\'$line[0]\' = \'$line[1]\'\n";
	$sample_id     				= $line[1] if $line[0] eq 'sample-id';
	$mutations_file = $line[1] if $line[0] eq 'mutations-file';

}


my $vcf_out = Vcf->new($sample_id);
$vcf_out->add_columns($id);
$vcf_out->add_header_line({key=>'FORMAT',ID=>'GT',Number=>'1',Type=>'String',Description=>"Genotype"});
print $vcf_out->format_header();

