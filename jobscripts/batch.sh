#!/bin/bash
envtypes=('W1905' 'W2095' 'C285' 'C867' 'ndepp5')
runtype='SASU'
for envtype in ${envtypes[@]}; do
    echo "submitting "$envtype"_"$runtype" ...."
    file="envfiles/"$envtype"_"$runtype".env"
    logfile="logfiles/"$envtype"_"$runtype".log"
    bash run_ens.sh $file > $logfile
done
