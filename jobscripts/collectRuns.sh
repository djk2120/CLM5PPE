#!/bin/bash

if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./collectRuns.sh mainrun.env"
    exit 1
fi

source $1

if [ ! -d $OUTPUT_DIR ]
then 
    mkdir $OUTPUT_DIR
fi


cd $SCRIPTS_DIR$casePrefix

ncases=$(ls | wc -w)
for i in $(seq -f "%03g" 1 $ncases)
do
    p=$casePrefix"_"$i
    echo $p
    cd $p
    keyfile=$p"_key.txt"
    d=$SCRATCH$p"/run/"

    while read -r line; do 
	tmp=(${line///}) 
	paramkey=${tmp[1]} 
	instkey=${tmp[0]}

	oldfile=$d$p".clm2_"$instkey".h0.*"
	newfile=$OUTPUT_DIR$paramkey"_h0.nc"
	cp $oldfile $newfile

	oldfile=$d$p".clm2_"$instkey".h1.*"
	newfile=$OUTPUT_DIR$paramkey"_h1.nc"
	cp $oldfile $newfile
    done < $keyfile
    cd ..
done
