#!/bin/bash
#PBS -N basecase
#PBS -q regular
#PBS -l walltime=2:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1

ks='/glade/work/oleson/PPE.n11_ctsm5.1.dev030_djk2120/cime/scripts/'
scratch="/glade/scratch/djk2120/"
keiths=('ctsm51c8BGC_PPEn11ctsm51d030_2deg_GSWP3V1_Sparse400_Control_1850AD' \
'ctsm51c8BGC_PPEn11ctsm51d030_2deg_GSWP3V1_Sparse400_Control_1850_step3' \
'ctsm51c8BGC_PPEn11ctsm51d030_2deg_GSWP3V1_Sparse400_Control_1850_step4' \
'ctsm51c8BGC_PPEn11ctsm51d030_2deg_GSWP3V1_Sparse400_part1_Control_hist')


s='/glade/work/djk2120/PPEn11trans/cime/scripts/'
casedir=$s"transient/basecases/"
cases=('PPEn11_transient_AD' \
'PPEn11_transient_SASU' \
'PPEn11_transient_postSASU' \
'PPEn11_transient')


cd $s


for i in "${!keiths[@]}"; do
    k=$ks${keiths[$i]}
    c=$casedir${cases[$i]}
    
    ./create_clone --case $c --clone $k --project P93300641 --cime-output-root /glade/scratch/djk2120
    cd $c
    ./case.setup
    ./xmlchange JOB_WALLCLOCK_TIME="12:00:00"
    ./xmlchange DOUT_S=False
    ./case.build
    echo -e "paramfile = '/glade/p/cgd/tss/people/oleson/modify_param/ctsm51_params.c210507_kwo.c220322.nc'">>user_nl_clm

    cd -
done
