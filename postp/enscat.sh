#!/bin/bash
#PBS -N enscat
#PBS -q casper
#PBS -l walltime=12:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1

module load nco
source ~/.bashrc
conda activate ppe-py

mkdir tmp

files=""
while read exp; do
    d='/glade/campaign/asp/djk2120/PPEn11/'$exp'/postp/'
    i=0
    while read p; do
	((i++))
	if [ $i -gt 1 ]; then
            arrp=(${p//,/ })
            f1=$d*${arrp[1]}*'.nc'
            f2=$d*${arrp[2]}*'.nc'
	    
	    ii=$(printf "%03d" $i)
	    
            ncecat -u minmax $f1 $f2 'tmp/param'$ii'.nc'
	fi
    done <survkey.csv

    ncecat -u param tmp/*.nc $exp".nc"
    rm tmp/*.nc

    files=$files" "$exp".nc"

done<exps.txt
ncecat -u exp $files OAAT.nc
rm $files


#label the new dimenions
# and append a couple extra vars
python label.py
rm OAAT.nc
rm -r tmp