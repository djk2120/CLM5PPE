#!/bin/bash
prevcase=$1
thiscase=$2
scratch="/glade/scratch/djk2120/"

cd $thiscase
#handle finidat
if [ $prevcase != 'none' ]; then

    #find the appropirate restart file
    casename=${prevcase##*/}
    echo $casename

    d=$scratch$casename'/run/'
    lastyr=-1
    restart="missing"
    for r in $d*clm2.r.*; do
	yr=$(echo $r | cut -d- -f1 | cut -d. -f4)
	if [[ $((10#$yr)) > $lastyr ]]; then
	    restart=$r
	fi
    done
    echo $restart

    if [ -f $restart ]; then
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
	echo -e 'finidat="'$restart'"'>>user_nl_clm
    else
	echo "ERROR: MISSING RESTART FILE"
	exit 1
    fi
fi
