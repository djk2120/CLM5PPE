#!/bin/bash
#PBS -N ens_submit
#PBS -q premium
#PBS -l walltime=12:00:00
#PBS -A P93300641
### Merge output and error files
#PBS -j oe
#PBS -k eod
### Select one CPU
#PBS -l select=1:ncpus=1

template='PPEn11/configs/template.config'
ensembles=('AF1855' 'C867' 'NDEP' 'AF2095')
suffs=('_SASU_' '_postSASU_' '_')


while read p; do

    for ensemble in ${ensembles[@]}; do

	for suff in ${suffs[@]};do
	    case='PPEn11_'$ensemble$suff$p
	    cd "/glade/scratch/djk2120/"$case"/run/"
	    rm *.h0.*
	done
    done

done < PPEn11/phen.txt
