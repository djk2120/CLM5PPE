#!/bin/bash
SCRIPTS_DIR="/glade/work/djk2120/ctsm_hardcode_co/cime/scripts/"
SPINDIR="/glade/scratch/djk2120/mini_ens/"
SCRATCH="/glade/scratch/djk2120/"
cd $SCRIPTS_DIR
for i in $(seq -f "%03g" 1 1)
do
    p="run_"$i
    echo $p
    cd $p
    keyfile=$p"_key.txt"
    d=$SCRATCH$p"/run/"

    while read -r line; do 
	tmp=(${line///}) 
	paramkey=${tmp[1]} 
	instkey=${tmp[0]}

	oldfile=$d$p".clm2_"$instkey".h0.0001-02-01-00000.nc"
	newfile=$SPINDIR$paramkey"_h0.nc"
	cp $oldfile $newfile

	oldfile=$d$p".clm2_"$instkey".h1.0001-02-01-00000.nc"
	newfile=$SPINDIR$paramkey"_h1.nc"
	cp $oldfile $newfile


    done < $keyfile
    cd ..
done
