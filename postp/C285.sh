#!/bin/bash
#PBS -N C285
#PBS -q casper
#PBS -l walltime=12:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1

source ~/.bashrc
conda activate ppe-py

d='/glade/campaign/asp/djk2120/PPEn11/C285/hist/'
for f in $d*"OAAT"*"h0"*".nc"; do
    echo $f
    python postp.py $f
done



