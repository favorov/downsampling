#!/usr/bin/perl -w 
#****************************************************************************
#mutation-call-by-coverage
#$Id: cheapseq.cpp 1810 2012-11-14 23:48:38Z favorov $
#****************************************************************************
# File name system: the work foder is where everything but the results is.
# the results folder is for results
#
#


use strict;

sub unlink_first_if_it_is_older($$);
sub downsampled_file_name($$);
sub repeat_file_name($$);
sub isnumber($);
sub isnatural($);

my $cheapseq_folder="../cheapseq";
my $downSAM_folder="../downSAM";
my $report2vcf_folder=$cheapseq_folder;
my $bowtie_folder="../../tools-src/bowtie/src/bowtie-0.12.8";
my $samtools_folder="../../tools-src/samtools/samtools-0.1.18";
my $bcftools_folder="$samtools_folder/bcftools";
my $vcftools_folder="../../tools-src/vcftools/vcftools/cpp";
my $bgzip_folder="../../tools-src/tabix/tabix-0.2.6";
my $results_folder="./results";

mkdir $results_folder if (! -d $results_folder);

my $argc = @ARGV;

print "\ncovearage.pl runs the coverage-testing pipeline .\n
Usage: perl coverage config-file\n" and exit if ($argc!=1); 

print "\ncovearage.pl runs the coverage-testing pipeline on a config file.\n
Usage: perl report2vcf config-file\n
The main name is sample_name. The default is: fasta_name_base-cheapseq-m1000-c5000-r100 that means:
fasta; mutation rate is 1 to 1000; coverage 5000 with reads of lemgth 100.
We also recommend to name the file itself with the sample_name.

First, it tests whether the reads and mutation files exist and if they are newer than config.
If no, it runs cheapseq config-file to emulate the sequencing procedure.
The names for reads and mutations are formed as: sample_name.reads; sample_name.mutations.
If there are reads_file and mutations_file tags in the config, the names are linked symbolically.

Then, the mutations_file is recoded into vcf format.
If mutations file is newer that its vcf form or the latter does not exist, rewrite vcf.
The vcf file name is mutations_file field from config with \".vcf\" suffix.

If there is no bowtie index (bowtie_index_base is to be in config), we biuld it from fasta_file.

Now, we want to align the reads aginst the fasta and to make basecalling. 
If there is no reads_file.bam file or it is older
than the read file, we run bowtie | samtools to align reads against the index and write bam file.
If there is not reads_file.vcf or it is older than the bam, samtools+bcftools make basecalling 
from the bam file write ruslts to reads_file.vcf .

Then, we compare the basecalled vcf and the mutation vcf with vcftools. The name for the result is
the sample_name and it lives in the results folder.

If we wave a downasmple schedule (like downsample_schedule=1,2,5 - the denominators for reads number), 
we sample the reads file according to it and repeat alignment+basecalling.
The number of downsample cycles is downsample_replica. 
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

my ($fasta_file, $sample_id, $mutations_file, $reads_file, $bowtie_index_base, $downsample_replica);

my ($mut_bases_per_snv,$read_length,$coverage); 

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
	$mut_bases_per_snv = $line[1] if $line[0] eq 'bases_per_snv';
	$read_length = $line[1] if $line[0] eq 'read_length';
	$coverage = $line[1] if $line[0] eq 'coverage';
	$reads_file = $line[1] if $line[0] eq 'reads_file';
	$mutations_file = $line[1] if $line[0] eq 'mutations_file';
	$bowtie_index_base= $line[1] if $line[0] eq 'bowtie_index_base';
	if ($line[0] eq 'downsample_schedule')
	{
		@downsample_schedule=split ',|;',$line[1];
		for (my $i=0;$i<=$#downsample_schedule;$i++)
		{
			die "Noniteger in downsample_schedule: $downsample_schedule[$i].\n" if ($downsample_schedule[$i] !~ /^\d+$/);
		}
	}
}
close CONFIG;

#process config

print "I cannot work without fasta filename.\n" and exit unless defined $fasta_file;
print "The fasta file $fasta_file is bot readable.\n" and exit unless -r $fasta_file;

if (!defined $read_length)
{
	print "Read length is set to 100 by default.\n";
	$read_length=100;
}
else
{
	print "Read length is not natural.\n" and exit unless isnatural $read_length;
}

if (!defined $coverage)
{
	print "Coverage is set to 100 by default.\n";
	$coverage=100;
}
else
{
	print "Coverage is not natural.\n" and exit unless isnatural $read_length;
}

if (!defined $mut_bases_per_snv)
{
	print "Number of bases per mutated SNV is set to 1000 by default.\n";
	$coverage=1000;
}
else
{
	print "Number of bases per mutated SNV is not natural.\n" and exit unless isnatural $read_length;
}

$fasta_file=~/^(.*)(\.fa|\.fa.gz)/;

my $fasta_name_base=$1;

if (! defined $bowtie_index_base)
{
	print "#Bowtie index base is supposed to be $fasta_name_base.\n";
	$bowtie_index_base=$fasta_name_base;
}

my $recommended_sample_id=$fasta_name_base."-cheapseq-m".$mut_bases_per_snv."-c".$coverage."-r".$read_length;

if (! defined $sample_id)
{
	print "#Sample is is constructed as $fasta_name_base.\n";
	$sample_id=$recommended_sample_id;
}
else #defined
{
	print "#The sample_id $sample_id differs from the recommended $recommended_sample_id.\n" 
		if not $sample_id eq $recommended_sample_id;
}

print "#Config file name $cfile_name does not start with the sample_id $sample_id.\n" if ($cfile_name!~/^$sample_id.*$/);

#filenames
my ($mutations_file_link,$reads_file_link);

$mutations_file_link= $mutations_file if defined $mutations_file;
$reads_file_link = $reads_file if defined $reads_file;

$mutations_file="$sample_id.mutations";
$reads_file="$sample_id.reads";

print "#Random coverage mutation test pipeline started. Config file is $ARGV[0], sample id is $sample_id.\n";
if (! -e $mutations_file || ! -e $reads_file) 
{
	unlink "$sample_id.rnd";
	my $cheapseq_string="$cheapseq_folder/cheapseq --cheapseq.reads_file $reads_file --cheapseq.mutations_file $mutations_file --cheapseq.random_state_file $sample_id.rnd $cfile_name";
	print "#Start cheapseq...\n";
	system($cheapseq_string) == 0 or die ("Cheapseq start failed: $?\n");
	print "#Finished (cheapseq) ...\n";
}
else
{
	print "#Mutations file and read files exist.\n";
}

if (defined $reads_file_link)
{
	symlink $reads_file,$reads_file_link;
}

if (defined $mutations_file_link)
{
	symlink $mutations_file,$mutations_file_link;
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
	my $report2vcf_string="perl -I $report2vcf_folder $report2vcf_folder/report2vcf.pl $mutations_file | $bgzip_folder/bgzip > $vcf_mutations_file.gz";
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



# here, we will start the internal cycles of the pipeline. It can be a cycle, do now we just include it in {}

{
	my $alingment_file_name=$sample_id;
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
		print "#Alignment is already build.\n";
	}


	#here, the downsample cycle starts
	#file name standards:
	#downsampled_file_name($mutations_file,$downsample_schedule[$i]),"\n";
	#repeat_file_name(downsampled_file_name($mutations_file,$downsample_schedule[$i]),12),"\n";

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
		#vcf only
		#./samtools mpileup -uf chr1_gl000192_random.fa.gz buegyrshlopak.bam | ./bcftools view -cvg - > mapped.calls-bue.vcf 
		#vcf and bcf 
		#./samtools mpileup -uf chr1_gl000192_random.fa.gz buegyrshlopak.bam | ./bcftools view -bcvg - > mapped.calls-bue.bcf 
		#./bcftools view mapped.calls-bue.bcf > mapped.calls-bue.vcf
	}
	else
	{
		print "#Basecalling is already done.\n";
	}
	print("#Calculate differences ...");
	system("$vcftools_folder/vcftools --gzdiff $vcf_mutations_file.gz --gzvcf $alingment_file_name.vcf.gz --out $results_folder/$alingment_file_name > /dev/null");
#	system("$vcftools_folder/vcftools --gzdiff $vcf_mutations_file.gz --gzvcf $alingment_file_name.vcf.gz --diff-site-discordance --out $alingment_file_name.diff");
	print(" done.\n");
}


#service functions
sub unlink_first_if_it_is_older($$)
{
	my ($vcf_mutations_file,$mutations_file)=@_;
	my $vcf_write_secs = (stat($vcf_mutations_file))[9];
	my $mut_write_secs = (stat($mutations_file))[9];
	unlink $vcf_mutations_file if $vcf_write_secs<$mut_write_secs;
}



sub downsampled_file_name($$)
{
	my ($namebase,$sampling_rate)=@_;
	return $namebase."_down_by_".$sampling_rate;
}

sub noised_file_name($$)
{
	my ($namebase,$sampling_rate)=@_;
	return $namebase."_noised_by_".$sampling_rate;
}

sub repeat_file_name ($$)
{
	my ($namebase,$repeat)=@_;
	return $namebase."_rep_".$repeat;
}

sub isnumber($){
	my ($string) = @_;
	 return 1 if ($string=~/^([+-]?)(?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?$/);
	return 0;
}

sub isnatural($){
	my ($string) = @_;
	 return 1 if ($string=~/^(\+?)\d+$/);
	return 0;
}

