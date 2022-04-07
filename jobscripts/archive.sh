#!/bin/bash

if [ $# -lt 2 ]
then
    echo "ERROR: please specify format file and whether to move files"
    echo "   ex: ./archive.sh CTL2010.config 0"
    exit 1
fi


:>collisions.txt

#set up environment variables
source $1
moveFiles=$2

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
	restdir=$REST
	
	#find restart from existing case
	olddir=$SCRATCH$case"_"$p"/run/"
	r=$(echo $olddir*".clm2.r."*)
	
	if [ -f $r ]; then  
	    #restart exists
	    f=$(basename $r)
	    bash ./move.sh $f $olddir $restdir $moveFiles
	    
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
    
    
