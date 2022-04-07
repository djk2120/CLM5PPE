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

template='PPEn11/configs/template.config'
ensembles=('C285' 'AF1855' 'C867' 'NDEP' 'AF2095')
chunk="phen"

for ensemble in ${ensembles[@]}; do

    #create new config file
    config='./PPEn11/configs/'$ensemble"_"$chunk".config"
    cp $template $config
    sed -i -e 's:CTL2010:'$ensemble':g' $config
    sed -i -e 's:chunk:'$chunk':g' $config
    
    #submit ensemble
    bash run_ens.sh $config

done
