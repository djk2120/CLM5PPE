#!/bin/bash

if [ $# -lt 2 ]
then
    echo "ERROR: please specify format file and whether to move files"
    echo "   ex: ./archive.sh CTL2010.config 0"
    exit 1
fi


#set up environment variables
source $1
moveFiles=$2

#moveFiles==0, don't move files, just check for restarts
#moveFiles==1, mv only if you won't overwrite
#moveFiles==2, mv with overwrite

#place to track collisions
:>collisions.txt

#create directories
dirs=($HIST $SPIN $REST)
for d in ${dirs[@]}; do
    mkdir -p $d
done

#loop through simulations
nc=${#cases[@]}
while read p; do
    missing=0
    i=0
    for case in ${cases[@]};do
	((i++))
	
	if (( i < $nc)); then
	    newdir=$SPIN
	else
	    newdir=$HIST
	fi
	
	#find clm restart from existing case
	olddir=$SCRATCH$case"_"$p"/run/"
	r=$(echo $olddir*".clm2.r."*)
	
	if [ -f $r ]; then  	    #restart exists
	    #archive restart
	    f=$(basename $r)
	    bash ./move.sh $f $olddir $REST $moveFiles
	    
	    #archive all hfiles
	    h=$(echo $olddir*".h*.*")
	    htapes=($(ls $h))
	    for htape in ${htapes[@]};do
		f=$(basename $htape)
		bash ./move.sh $f $olddir $newdir $moveFiles
	    done
	else
	    #restart missing
	    echo "MODEL CRASH?:"$case"_"$p" is missing restart"
	    ((missing++))
	fi
	
    done
    if [ $missing -eq 0 ]; then
	echo $case"_"$p" generates restarts"
    fi
done<$paramList


collisions=$(wc -l < collisions.txt)
if [[ $collisions > 0 ]]; then
    echo $collisions" files already existed in the archive"
    if [[ $moveFiles -lt 2 ]]; then
	echo "Those files were NOT overwritten"
    else
	echo "Those files were overwritten"
    fi
    echo "see collisions.txt for file list"
fi

