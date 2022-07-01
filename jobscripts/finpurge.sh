#!/bin/bash
prevcase=$1
scratch=$2
thiscase=$3

cd $thiscase
#handle finidat
if [ $prevcase != 'none' ]; then

    #find the previous restart file
    casename=${prevcase##*/}
    pd=$scratch$casename'/run/'
    restart=$pd$casename".clm2.r."*".nc"
    restart=$(echo $restart) #expands wildcard

    #move to a restarts folder in scratch
    arr=(${casename//_/ })
    codebase=${arr[0]}
    td="/glade/scratch/djk2120/"$codebase"_restarts/"
    if [ ! -d $td ]; then
	mkdir -p $td
    fi
    r2=$td$(basename $restart)
    cp $restart $r2

    #remove all netcdfs from prevcase (DANGER)
    rm $pd"*.nc"

    #point to restart file in user_nl_clm
    if [ -f $r2 ]; then
    	#comment out any finidat from user_nl_clm
    	:> user_nl_clm.tmp
    	while read line; do
    	    if [[ $line != *"finidat"* ]]; then
    		echo $line>>user_nl_clm.tmp
    	    else
    		echo '!'$line>>user_nl_clm.tmp
    	    fi
    	    done<user_nl_clm
    	mv user_nl_clm.tmp user_nl_clm
	
    	#append to user_nl_clm
    	echo -e 'finidat="'$r2'"'>>user_nl_clm
    else
    	exit 1
    fi
fi
