#!/bin/bash
#PBS -N CTL2010
#PBS -q casper
#PBS -l walltime=12:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1

source ~/.bashrc
conda activate ppe-py

f='zqz'
python postp_lhc.py $f




