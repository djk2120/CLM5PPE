#!/bin/bash

#envtypes=('CTL2010' 'C285' 'AF1855')
#runtype='PROD'
#chunk='e0'
#


envtypes=('CTL2010' 'C285' 'AF1855' 'C867' 'NDEP' 'AF2095')
#envtypes=('C867' 'NDEP')
runtype='PROD'
chunk='claypf'
#tapes=('r')
tapes=('r' 'h0' 'h1' 'h2' 'h3' 'h4' 'h5' 'h7')


moveFiles=2

if [ $runtype == 'PROD' ];then
    runstr=''
    pad=''
else
    runstr=$runtype
    pad='_'
fi


for envtype in ${envtypes[@]}; do
    cfile="PPEn11/configs/"$envtype"_"$runstr$pad$chunk".config"
    echo $cfile
    for tape in ${tapes[@]}; do
	bash collect.sh $cfile $tape $moveFiles
    done

done
