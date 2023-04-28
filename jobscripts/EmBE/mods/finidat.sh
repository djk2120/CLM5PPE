#!/bin/bash
prevcase=$1
thiscase=$2
scratch="/glade/scratch/linnia/"

cd $thiscase
#handle finidat
if [ $prevcase != 'none' ]; then

    #find the appropirate restart file
    casename=${prevcase##*/}
    restart=$scratch$casename'/run/'$casename".clm2.r."*".nc"
    restart=$(echo $restart) #expands wildcard

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
	exit 1
    fi
fi
