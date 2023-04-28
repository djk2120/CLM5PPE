#!/bin/bash
# clone the existing transient basecases

source ~/.bashrc
conda activate runclm

CIMEROOT="/glade/work/linnia/PPEn11trans/cime/scripts/"
CLONEROOT="/glade/work/djk2120/PPEn11trans/cime/scripts/transient/basecases/"
CASEROOT="/glade/work/linnia/PPEn11trans/cime/scripts/transient/basecases/"

if [ ! -d $CASEROOT ]; then
    mkdir -p $CASEROOT
fi

case_list=("PPEn11_transient_AD" "PPEn11_transient_SASU" "PPEn11_transient_postSASU" "PPEn11_transient")

for case in ${case_list[@]}; do
	echo $case

	cd $CIMEROOT
	./create_clone --case $CASEROOT$case --clone $CLONEROOT$case --cime-output-root /glade/scratch/linnia
	cd $CASEROOT$case
	./case.setup

	if [ $case = "PPEn11_transient_AD" ]; then
		echo "found AD"
		f1='/glade/p/cgd/tss/people/oleson/CLM5_restarts/clm51_PPEn02ctsm51d021_2deg_GSWP3V1_leafbiomassesai_PPE3_1850pAD.clm2.r.2041-01-01-00000.nc'
		f2='/glade/u/home/djk2120/restarts/PPEn11_transient_postSASU_LHC0000.clm2.r.0041-01-01-00000.nc'

		sed -i 's:'$f1':'$f2':g' user_nl_clm
	fi

	if [ $case = "PPEn11_transient" ]; then
		./xmlchange DIN_LOC_ROOT_CLMFORC='/glade/p/cgd/tss/people/oleson'
        else 
                d1='/glade/scratch/oleson'
		d2='/glade/p/cgd/tss/people/oleson'
		sed -i 's:'$d1':'$d2':g' user_datm.*
	fi	
done

for case in ${case_list[@]}; do
        #echo 'building' $case
	cd $CASEROOT$case
	./case.build
done


