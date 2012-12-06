#!/usr/bin/perl -w 
#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
use strict;

sub unlink_first_if_it_is_older($$);
sub downsampled_alignment_file_name($$);
sub repeat_file_name($$);

my $cheapseq_folder="../cheapseq";
my $downSAM_folder="../downSAM";
my $report2vcf_folder=$cheapseq_folder;
my $bowtie_folder="../../tools-src/bowtie/src/bowtie-0.12.8";
my $samtools_folder="../../tools-src/samtools/samtools-0.1.18";
my $bcftools_folder="$samtools_folder/bcftools";
my $vcftools_folder="../../tools-src/vcftools/vcftools/cpp";
my $bgzip_folder="../../tools-src/tabix/tabix-0.2.6";
my $results_folder="results";

mkdir $results_folder if (! -d $results_folder);

my $argc = @ARGV;

print "\ncovearage.pl runs the coverage-testing pipeline .\n
Usage: perl coverage config-file\n" and exit if ($argc!=1); 

print "\ncovearage.pl runs the coverage-testing pipeline on a config file.\n
Usage: perl report2vcf config-file\n
First, it tests whether the Fasta with reads exist 
If no, it runs cheapseq config-file 
If mutations file is newer that its vcf form or the latter does not exist, rewrite vcf.
The vcf file name is mutation_file field from config with \".vcf\" suffix.
If there is no bowtie index (bowtie_index_base is to be in config), biuld it from fasta_file.
The reads_file name is known from config. If there is no reads_file.bam file or it is older
than the read file, we run bowtie | samtools to align reads against the index and write bam file.
If there is not reads_file.vcf or it is older than the bam, samtools+bcftools make basecalling 
from the bam file write ruslts to reads_file.vcf .


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

my ($fasta_file, $sample_id, $mutations_file, $reads_file, $bowtie_index_base);

my @downsample_schedule;

while (<CONFIG>) {
	chomp;
	s/\r//g;
	next if /^#/;
	my @line = split("=");
	$line[0] = "" if not defined $line[0];
	$line[1] = "" if not defined $line[1];

	#	print "\'$line[0]\' = \'$line[1]\'\n";
	$fasta_file	= $line[1] if $line[0] eq 'fasta_file';
	$sample_id 	= $line[1] if $line[0] eq 'sample_id';
	$reads_file = $line[1] if $line[0] eq 'reads_file';
	$mutations_file = $line[1] if $line[0] eq 'mutations_file';
	$bowtie_index_base= $line[1] if $line[0] eq 'bowtie_index_base';
	if ($line[0] eq 'downsample_schedule')
	{
		@downsample_schedule=split ',|;',$line[1];
		for (my $i=0;$i<=$#downsample_schedule;$i++)
		{
			die "Noniteger in downsample_schedule: $downsample_schedule[$i].\n" if ($downsample_schedule[$i] !~ /^\d+$/);
			print downsampled_alignment_file_name($mutations_file,$downsample_schedule[$i]),"\n";
			print repeat_file_name(downsampled_alignment_file_name($mutations_file,$downsample_schedule[$i]),12),"\n";
		}
	}
}

exit;
print "#Random coverage mutatition test pipeline. Config file is $ARGV[0], sample id is $sample_id.\n";

if (! -e $mutations_file || ! -e $reads_file) 
{
	my $cheapseq_string=$cheapseq_folder."/cheapseq";
	print "#Start cheapseq...\n";
	system($cheapseq_string,$cfile_name) == 0 or die ("Cheapseq start failed: $?\n");
	print "#Finished (cheapseq) ...\n";
}
else
{
	print "#Mutations file and read files exist.\n";
}

my $vcf_mutations_file=$mutations_file.".vcf";

if ( -e $vcf_mutations_file ) 
{
	unlink_first_if_it_is_older($vcf_mutations_file,$mutations_file);
	#vcf file is to be younger than mutations file
}

if ( ! -e $vcf_mutations_file ) 
{
	#my $report2vcf_string="perl -I $report2vcf_folder $report2vcf_folder."/report2vcf.pl";
	my $report2vcf_string="perl -I $report2vcf_folder $report2vcf_folder/report2vcf.pl $cfile_name | $bgzip_folder/bgzip > $vcf_mutations_file.gz";
	print "#Start report->vcf...\n";
	system($report2vcf_string) == 0 or die ("Report2vcf.pl start failed: $?\n");
	print "#Finished (report->vcf) ...\n";
}
else
{
	print "#Mutations file is already converted to vcf.\n";
}

if (! 
	(
		-e $bowtie_index_base.".1.ebwt"
		&&
		-e $bowtie_index_base.".2.ebwt"
		&&
		-e $bowtie_index_base.".3.ebwt"
		&&
		-e $bowtie_index_base.".4.ebwt"
		&&
		-e $bowtie_index_base.".rev.1.ebwt"
		&&
		-e $bowtie_index_base.".rev.2.ebwt"
	) 
)
{
	print "#Building Bowtie index...\n";
	my $gzipped=$fasta_file =~ /.*.gz/;
	my $fasta_ungzipped_file="";
	if ($gzipped)
	{
		print "#Gzipped FASTA\n";
		$fasta_ungzipped_file=substr $fasta_file, 0 , -3;
		system "gzip -dc $fasta_file > $fasta_ungzipped_file";
		print "#unGzipped ...\n";
		system("$bowtie_folder/bowtie-build $fasta_ungzipped_file $bowtie_index_base");
	}
	if ($gzipped)
	{
		unlink $fasta_ungzipped_file;
		print "#Unlink unGzipped ...\n"
	}
	print "#Finished (Biuld Bowtie index) ...\n";
}
else
{
	print "#Bowtie index is already build.\n";
}



# here, we will start the internal cycle of the pipeline. It can be a cyccle, do now we just include it in {}

{
	my $alingment_file_name=$reads_file;
	if ( -e $alingment_file_name.".bam")
	{
		unlink_first_if_it_is_older($alingment_file_name.".bam",$reads_file);
		#alignment is to be younger
	}
	if ( ! -e $alingment_file_name.".bam")
	{

		print("#Aligning reads with Bowtie\n");
		#./bowtie -S -v 2 -m 1 --un unmapped.tests.sam -f chr1_gl000192_random reads.test --sam-RG SM:quasiburroed 2> bowtie.log.test.sam | ./samtools view -Sbh -   >  mapped.test.bam
		system("$bowtie_folder/bowtie -S -v 2 -m 1 --un $alingment_file_name.unmapped --sam-RG SM:$sample_id -f $bowtie_index_base $reads_file 2> bowtie.$alingment_file_name.log > $alingment_file_name.sam");
		print("#sam->bam\n");
		system("$samtools_folder/samtools view -Sbh $alingment_file_name.sam > $alingment_file_name.bam");
		print "#Finished (alignment) ...\n";
		unlink "$alingment_file_name.sam";
	}
	else
	{
		print "#Aligning is already build.\n";
	}
#vcf only
#./samtools mpileup -uf chr1_gl000192_random.fa.gz buegyrshlopak.bam | ./bcftools view -cvg - > mapped.calls-bue.vcf 
#vcf and bcf 
#./samtools mpileup -uf chr1_gl000192_random.fa.gz buegyrshlopak.bam | ./bcftools view -bcvg - > mapped.calls-bue.bcf 
#./bcftools view mapped.calls-bue.bcf > mapped.calls-bue.vcf
	if ( -e $alingment_file_name.".vcf.gz")
	{
		unlink_first_if_it_is_older($alingment_file_name.".vcf.gz",$alingment_file_name.".bam");
		#vcf is to be younger
	}
	if ( ! -e $alingment_file_name.".vcf.gz")
	{
		print("#Make basecalling\n");
		system("$samtools_folder/samtools mpileup -uf $fasta_file $alingment_file_name.bam > $alingment_file_name.pileup");
		print("#pileup->vcf\n");
		system("$bcftools_folder/bcftools view -cvg $alingment_file_name.pileup | $bgzip_folder/bgzip > $alingment_file_name.vcf.gz");
		print "#Finished (basecalling) ...\n";
		unlink "$alingment_file_name.pileup"
	}
	else
	{
		print "#Basecalling is already done.\n";
	}
	system("$vcftools_folder/vcftools --gzdiff $vcf_mutations_file.gz --gzvcf $alingment_file_name.vcf.gz --out $alingment_file_name.diff");
#	system("$vcftools_folder/vcftools --gzdiff $vcf_mutations_file.gz --gzvcf $alingment_file_name.vcf.gz --diff-site-discordance --out $alingment_file_name.diff");
}


#service functions
sub unlink_first_if_it_is_older($$)
{
	my ($vcf_mutations_file,$mutations_file)=@_;
	my $vcf_write_secs = (stat($vcf_mutations_file))[9];
	my $mut_write_secs = (stat($mutations_file))[9];
	unlink $vcf_mutations_file if $vcf_write_secs<$mut_write_secs;
}

sub downsampled_alignment_file_name($$)
{
	my ($namebase,$sampling_rate)=@_;
	return $namebase."_down_by_".$sampling_rate;
}

sub repeat_file_name ($$)
{
	my ($namebase,$repeat)=@_;
	return $namebase."_rep_".$repeat;
}
