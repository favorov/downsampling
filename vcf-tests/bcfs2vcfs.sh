#!/bin/bash

bcfs='bcfs'
vcfs='vcfs'

mkdir -p ${vcfs}

for i in ${bcfs}/*.bcf
do
	shortfilename=${i##*/}
	echo $shortfilename "--->" ${vcfs}/${shortfilename/.bcf/.vcf}
  bcftools view $i > ${vcfs}/${shortfilename/.bcf/.vcf}
done
