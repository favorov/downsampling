#!/usr/bin/perl -w 
#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
use strict;
use vcftools_pm::Vcf;

my $argc = @ARGV;

print STDERR "\nreport2vcf.pl converts the mutation report that was genarated by cheapseq to vcf format.\n
Usage: perl report2vcf mutations_file [sample_id]\n" and exit if ($argc!=1); 

print "\nreport2vcf.pl converts the mutation report that was genarated by cheapseq to vcf format.\n
Usage: perl report2vcf mutations-file sample_id\n
mutations-file is obligatory 
sample_id is optional is mutations-file has format something.mutations, sample_id will be something\n\n
" and exit if 
(
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
	)
	or $argc==0
	or $argc>2 
);

my $mutations_file = $ARGV[0];

my $sample_id;

if ($argc==2)
{
	$sample_id=$ARGV[1];
}
else
{
	if ($mutations_file=~/^(.+)\.mutations$/)
	{
		$sample_id=$1;
	}
	else
	{
		print STDERR "Cannot get sample_id from parameters.\n";
		exit;
	}
}
;


open( MUTAT, $mutations_file) or print STDERR "Can't open mutations file $mutations_file: $!\n" and exit;

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
output_model_mut_to_vcf($chrom,$pos,$sample_id,$ref,[$alt]) if (!$prev_line_logged_to_vcf);
#the last line. We are not to frgrt it.

# chrom, pos, id, ref, alt_list (ref to a list)
sub output_model_mut_to_vcf
{
	my ($chrom,$pos,$id,$ref,$alt_list_ref)=@_;
	my %out;
	my $snp;
	#print "out call: $chrom:$pos:$id:$ref:",join(",",@$alt_list_ref),"\n";
	#return;
	my $ucref=uc $ref;
	my @ucalt=();	
	push @ucalt, uc foreach @$alt_list_ref;
	#the ref and the altlist are both moved to uppercase;
	#hstcmd like its two vcf's to have the came case of ref and alt fields
	$out{CHROM}  = $chrom;
	$out{POS}    = $pos;
	
	$out{ID}     = '.';
	$out{ALT}    = \@ucalt;
	$out{REF}    = $ucref;
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
