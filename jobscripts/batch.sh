#!/bin/bash
#PBS -N fivens
#PBS -q regular
#PBS -l walltime=12:00:00
#PBS -A P93300041
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1


exps=('C285' 'C867' 'AF1855' 'AF2095' 'NDEP')
for exp in ${exps[@]}; do
    bash run_ens.sh "PPEn11/"$exp"_qc3.config"
done
