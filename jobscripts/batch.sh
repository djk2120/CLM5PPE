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



#envtypes=('C867')
#envtypes=('NDEP')
envtypes=('CTL2010' 'C285' 'AF1855' 'C867' 'NDEP' 'AF2095')
runtype='PROD'
chunk='claypf'

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
