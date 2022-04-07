#!/bin/bash
#PBS -N ensemble_phen
#PBS -q premium
#PBS -l walltime=12:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1

#simple script to rebuild all my basecases

envtypes=('CTL2010' 'C285' 'AF1855' 'C867' 'NDEP' 'AF2095')
suffs=('_AD' '_SASU' '_postSASU' '/')
s="/glade/work/djk2120/PPEn11/cime/scripts/"
cb="PPEn11"

PWD=$(pwd)


for suff in ${suffs[@]}; do
    for envtype in ${envtypes[@]}; do
	d=$s$envtype"/basecases/"
	c=$cb"_"$envtype$suff
	
	echo "---------------------------------------------"
	echo "   rebuilding "$c
	echo "---------------------------------------------"
	cd $d$c
	./case.build
    done
done
