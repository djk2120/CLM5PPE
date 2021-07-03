#!/bin/bash
if [ $# -eq 0 ]
then
    echo "ERROR: please specify the runtype"
    echo "   ex: ./cloneZZ.sh SASU"
    exit 1
fi

runtype=$1
envtype="CTL2010"
base="ctsm51c6_PPEn08ctsm51d023_2deg_GSWP3V1_Sparse400_2000"
keithdir='/glade/work/oleson/PPE.n08_ctsm5.1.dev023/cime/scripts/'
scripts='/glade/work/djk2120/PPEn08/cime/scripts/'
scratch='/glade/scratch/djk2120'
nlbase='/glade/u/home/djk2120/clm5ppe/jobscripts/PPEn08/nlbase/basecases/'
envdir=$envtype"/basecases/"


if [[ $runtype == "AD" ]];then 
    stopn=20
    basecase=$keithdir$base"AD"
    echo $basecase
fi

if [[ $runtype == "SASU" ]];then 
    stopn=80
    prevtype="AD"
    nyprev="21"
    basecase=$keithdir$base"_step3"
    echo $basecase
fi

if [[ $runtype == "postSASU" ]];then 
    stopn=40
    prevtype="SASU"
    nyprev="81"
    basecase=$keithdir$base"_step4"
    echo $basecase
fi

if [[ $runtype == "PROD" ]];then 
    stopn=10
    prevtype="postSASU"
    nyprev="41"
    basecase=$keithdir$base
    echo $basecase
fi

newcase="PPEn08_"$envtype"_"$runtype
prevcase="PPEn08_"$envtype"_"$prevtype

cd $scripts
pwd


echo "basecase="$basecase
echo "nextcase="$envdir$newcase

./create_clone --case $envdir$newcase --clone $basecase --cime-output-root $scratch

cd $envdir$newcase
./case.setup
#./case.build

cp $nlbase$runtype".base" user_nl_clm
./xmlchange STOP_N=$stopn
./xmlchange JOB_QUEUE="economy"
./xmlchange DOUT_S="false"
./xmlchange PROJECT="P08010000"

#consider using just one nlbase
#and appending appropriate finidat and paramfile

if [[ $runtype != "AD" ]];then
    scratch="/glade/scratch/djk2120/"$prevcase"/run/"
    suffix=".clm2.r.00"$nyprev"-01-01-00000.nc"
    restart=$scratch$prevcase$suffix
    echo "finidat = '"$restart"'" >> user_nl_clm
fi

if [[ $envtype == "nddep5" ]];then
    echo "stream_fldfilename_ndep = '/glade/p/cgd/tss/people/oleson/CLM5_ndep/fndep_p5_clm_hist_b.e21.BWHIST.f09_g17.CMIP6-historical-WACCM.ensmean_1849-2015_monthly_0.9x1.25_c180926.nc'">> user_nl_clm
fi
