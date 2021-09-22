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



envtypes=('NDEP' 'C867' 'AF2095')
runtype='AD'
chunk='e0'

if [ $runtype == 'PROD' ];then
    runstr=''
    pad=''
else
    runstr=$runtype
    pad='_'
fi


for envtype in ${envtypes[@]}; do

    echo "submitting "$envtype"_"$runstr$pad$chunk" ...."
    bash make_config.sh $envtype $runtype $chunk
    cfile="PPEn11/configs/"$envtype"_"$runstr$pad$chunk".config"
    lfile="logfiles/"$envtype"_"$runstr$pad$chunk".log"
    bash run_ens.sh $cfile > $lfile

done
