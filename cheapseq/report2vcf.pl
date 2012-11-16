#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
#!/usr/bin/perl -w 
use strict;
use vcftools::Vcf;

my $argc = @ARGV;

print "\nreport2vcf.pl converts the mutation report that was genarated by cheapseq to vcf format.\n
Usage: perl report2vcf config-file\n" and exit if ($argc!=1); 

print "\nreport2vcf.pl converts the mutation report that was genarated by cheapseq to vcf format.\n
Usage: perl report2vcf config-file\n
understands two lines:
mutations_file = mutations-file-name
sample_id = name-of-sample\n\n
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

open( CONFIG, $ARGV[0] ) or print "Can't open config file $ARGV[0]: $!\n" and exit;

my ($sample_id,$mutations_file);

while (<CONFIG>) {
	chomp;
	s/\r//g;
	next if /^#/;
	my @line = split("=");
	$line[0] = "" if not defined $line[0];
	$line[1] = "" if not defined $line[1];

	#	print "\'$line[0]\' = \'$line[1]\'\n";
	$sample_id     				= $line[1] if $line[0] eq 'sample_id';
	$mutations_file = $line[1] if $line[0] eq 'mutations_file';
}

close CONFIG;

open( MUTAT, $mutations_file) or print "Can't open mutations file $mutations_file: $!\n" and exit;

my $vcf_out = Vcf->new();
$vcf_out->add_columns($sample_id);
$vcf_out->add_header_line({key=>'FORMAT',ID=>'GT',Number=>'1',Type=>'String',Description=>"Genotype"});
print $vcf_out->format_header();


my ($prev_pos,$prev_thread)=(-1,-1);

while(<MUTAT>)
{
	chomp;
	s/\r//g;
	next if /^#/;
	my @line = split(":");
	my $one_thread = undef;
	my $output = ;

	my %out;
	$out{CHROM}  = $line[0];
	$out{POS}    = $line[2];
	
	$out{ID}     = '.';
	$out{ALT}    = [];
	$out{REF}    = $refseq->get_base($chr,$pos);
	$out{QUAL}   = '.';
	$out{FILTER} = ['.'];
	$out{FORMAT} = ['GT'];
	$snp = "$1/$2";
	$out{gtypes}{$id}{GT} = $snp;

	$vcf_out->format_genotype_strings(\%out);
	print $vcf_out->format_line(\%out);
}
close(MUTAT);
