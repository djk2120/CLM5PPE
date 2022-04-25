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
ensembles=('C285' 'AF1855' 'C867' 'NDEP' 'AF2095')
suffs=('_AD_' '_SASU_' '_postSASU_' '_')

:>tmp.txt
while read p; do
    t=$p','
    for ensemble in ${ensembles[@]}; do
	missing=0
	for suff in ${suffs[@]};do
	    case='PPEn11_'$ensemble$suff$p
	    f='/glade/scratch/djk2120/'$case'/run/*.clm2.r.*'
	    if [[ missing -eq 0 ]]; then
		if [ ! -f $f ]; then
		    missing=1
		    t=$t$case','
		fi
	    fi
	done
    done
    echo $t >> tmp.txt
done < PPEn11/phen.txt
