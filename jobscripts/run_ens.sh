#!/bin/bash
if [ $# -lt 1 ]
then
    echo "ERROR: please specify config file"
    echo "   ex: ./runens.sh CTL2010_chunk1.config"
    exit 1
fi

#set up environment variables
source $1

#this file will hold the list of tethered jobs
joblist='joblist.txt' 

if [ "$tetherFlag" = false ]
then
    cases=($basecase)
fi

while read p; do
    for case in ${cases[@]}; do

	basecase=$SCRIPTS$ensemble"/basecases/"$case
	thiscase=$SCRIPTS$ensemble"/"$case"/"$case"_"$p
	
	cd $SCRIPTS
	./create_clone --case $thiscase --clone $basecase --keepexe

	cd $thiscase
	./case.setup
	./xmlchange DOUT_S=TRUE
	./xmlchange PROJECT=$PROJECT

	#comment out previous paramfile from user_nl_clm
	:> user_nl_clm.tmp
	while read line; do
	    if [[ $line != *"paramfile"* ]]; then
		echo $line>>user_nl_clm.tmp
	    else
		echo '!'$line>>user_nl_clm.tmp
	    fi
	done<user_nl_clm
	mv user_nl_clm.tmp user_nl_clm

	#append correct paramfile
	pfile=$PARAMS$p".nc"
	pfilestr="paramfile = '"$pfile"'"
	echo -e "\n"$pfilestr >> user_nl_clm
	
	# cat nlmods if needed
	if [ "$nlmodsFlag" = true ]
	then
	    nlmods=$NLMODS$p".txt"
	    cat $nlmods >> user_nl_clm
	fi


	if [ "$tetherFlag" = false ]
	then
	    ./case.submit -a "-l place=group=rack"
	fi

    done
done<$paramList
