#!/bin/bash

case=$1 
newdir=$2 
howsafe=$3
scratch=$4
fails=$5
collisions=$6


#howsafe
# 0 - check casedir, don't mv or cp
# 1 - mv, but don't overwrite
# 2 - mv, overwrite

casedir=$scratch$case"/run/"
restart=$casedir"*.clm2.r.*"

if [ -f $restart ]; then

    #mv restart to temp rdir
    arr=(${case//_/ })
    codebase=${arr[0]}
    rd="/glade/scratch/djk2120/"$codebase"_restarts/"
    f=$(basename $restart)
    if [ $howsafe -gt 0 ]; then
        bash move.sh $f $casedir $rd $howsafe $collisions
    fi
    
    #mv htapes to campaign
    h=$(echo $casedir*".h*.*")
    htapes=($(ls $h))
    for htape in ${htapes[@]};do
	f=$(basename $htape)
	if [ $howsafe -gt 0 ]; then
	    bash move.sh $f $casedir $newdir $howsafe $collisions
	fi
    done
else
    #keep track of cases without restarts
    echo $case >> $fails
fi




