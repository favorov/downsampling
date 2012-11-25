#!/usr/bin/perl -w 
#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
use strict;
use vcftools.pm::Vcf;

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


my ($chrom,$thread,$pos,$ref,$alt);

my $prev_line_logged_to_vcf=0; 

while(<MUTAT>)
{
	chomp;
	s/\r//g;
	next if /^#/;
	my ($cur_chrom,$cur_thread,$cur_pos,$cur_ref,$cur_alt) = split(":");
	#print "--->",join("::",($cur_chrom,$cur_thread,$cur_pos,$cur_ref,$cur_alt)),"\n";

	if ($prev_line_logged_to_vcf || !defined $chrom) #previous line was outputed or we just started 
	{
		($chrom,$thread,$pos,$ref,$alt)=($cur_chrom,$cur_thread,$cur_pos,$cur_ref,$cur_alt);
		#save the current line
		$prev_line_logged_to_vcf=0;
		next;
	}

	if
	(
		$cur_chrom ne $chrom
		||
		$cur_pos ne $pos
	)
	{
		#output $chrom:$pos:......., i.e. prev line
		#print "*";
		output_model_mut_to_vcf($chrom,$pos,$sample_id,$ref,[$alt]);
		($chrom,$thread,$pos,$ref,$alt)=($cur_chrom,$cur_thread,$cur_pos,$cur_ref,$cur_alt);
		#save the current line
		$prev_line_logged_to_vcf=0;
		next;
	}

	#if we are here, our current line and the prev line refer to the same chorm/pos, i.e. it is
	#a two-thread mutation. All the prev/current line stuff is to account for the situation correctly
	die "There are two mutations on the same thread at $chrom:$pos .\n" if $thread==$cur_thread;
	#test different threads
	die "There are two mutations with different reference at $chrom:$pos .\n" if $ref ne $cur_ref;
	#test same ref

	#print "+";
	output_model_mut_to_vcf($chrom,$pos,$sample_id,$ref,[$alt,$cur_alt]);
	$prev_line_logged_to_vcf=1;
}
close(MUTAT);

# chrom, pos, id, ref, alt_list (ref to a list)
sub output_model_mut_to_vcf
{
	my ($chrom,$pos,$id,$ref,$alt_list_ref)=@_;
	my %out;
	my $snp;
	#print "out call: $chrom:$pos:$id:$ref:",join(",",@$alt_list_ref),"\n";
	#return;
	$out{CHROM}  = $chrom;
	$out{POS}    = $pos;
	
	$out{ID}     = '.';
	$out{ALT}    = $alt_list_ref;
	$out{REF}    = $ref;
	$out{QUAL}   = '.';
	$out{FILTER} = ['.'];
	$out{FORMAT} = ['GT'];
	if (scalar(@$alt_list_ref)==1)
	{
		$snp = "0/1";
	}
	elsif(scalar(@$alt_list_ref)==2)
	{
		$snp = "1/2";
	}
	else 
	{	
		die "There are <1 or >2 alt's at $chrom:$pos .\n" 
	}
	$out{gtypes}{$id}{GT} = $snp;

	$vcf_out->format_genotype_strings(\%out);
	print $vcf_out->format_line(\%out);
}
