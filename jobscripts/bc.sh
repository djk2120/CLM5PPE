#!/bin/bash
envtypes=('CTL2010' 'C285' 'AF1855')

prevtype='postSASU'
chunk='s0'

mvfiles=$1

for envtype in ${envtypes[@]}; do
    cfile="PPEn11/configs/"$envtype"_"$prevtype"_"$chunk".config"
    echo $cfile
    echo "checking "$envtype"_"$prevtype"_"$chunk" restarts ...."
    bash check_restarts.sh $cfile $mvfiles

done
