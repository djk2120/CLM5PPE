#!/bin/bash
#PBS -N ens_submit
#PBS -q regular
#PBS -l walltime=12:00:00
#PBS -A P93300641
### Merge output and error files
#PBS -j oe
#PBS -k eod
### Select one CPU
#PBS -l select=1:ncpus=1


ensemble='AF2095'
chunk="phen"
joblist='tethered.txt' 

config='./PPEn11/configs/'$ensemble"_"$chunk".config"
source $config
ad=${cases[0]}
sasu=${cases[1]}
while read p; do
    prevcase=$SCRIPTS$ensemble"/"$ad"/"$ad"_"$p
    thiscase=$SCRIPTS$ensemble"/"$sasu"/"$sasu"_"$p
    bash tether.sh $prevcase $SCRATCH $thiscase $joblist $template
done<$paramList

