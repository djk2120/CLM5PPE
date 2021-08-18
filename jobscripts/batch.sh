#!/bin/bash
envtypes=('CTL2010' 'C285' 'AF1855')
runtype='PROD'
chunk='s0'

if [ $runtype == 'PROD' ];then
    runstr=''
    pad=''
else
    pad=' '
fi


for envtype in ${envtypes[@]}; do

    echo "submitting "$envtype"_"$runstr$pad$chunk" ...."
    bash make_config.sh $envtype $runtype $chunk
    cfile="PPEn11/configs/"$envtype"_"$runstr$pad$chunk".config"
    lfile="logfiles/"$envtype"_"$runstr$pad$chunk".log"
    bash run_ens.sh $cfile > $lfile

done
