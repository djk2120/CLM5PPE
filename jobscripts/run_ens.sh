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
    i=0
    prevcase="none"
    for basecase in ${cases[@]}; do
	((i++))

	case=$(basename $basecase)
	thiscase=$CASEDIR$case"/"$case"_"$p
	
	cd $SCRIPTS
	./create_clone --case $thiscase --clone $basecase --keepexe

	cd $thiscase
	./case.setup
	./xmlchange PROJECT=$PROJECT
	./xmlchange JOB_QUEUE="regular"
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

	#edit first case finidat if needed
	if [ "$finidatFlag" = true ]
	then
	    if [[ $i -eq 1 ]]; then
		bash $finidatScript $prevcase $SCRATCH $thiscase
	    fi
	fi

	# cat nlmods if needed
	if [ "$nlmodsFlag" = true ]
	then
	    nlmods=$NLMODS$p".txt"
	    cat $nlmods >> user_nl_clm
	fi


    done

    # submit case (with tethering if needed)
    if [ "$tetherFlag" = false ]
    then
	./case.submit -a "-l place=group=rack"
    else
	#tethering setup
	basecase="${cases[0]}"
	case=$(basename $basecase)
	firstcase=$CASEDIR$case"/"$case"_"$p
	cd $firstcase
	:> $joblist
	for i in "${!segments[@]}"; do  #loop through all steps/substeps
	    basecase="${segments[i]}"
	    case=$(basename $basecase)
	    casemod="${casemods[i]}"
	    thiscase=$CASEDIR$case"/"$case"_"$p
	    
	    echo -n $case"_"$p >> $joblist
	    echo -n ","$thiscase >> $joblist
	    echo -n ","$casemod >> $joblist
	    
	    if [ $i -eq 0 ]; then
		echo ",queued" >> $joblist
	    else
		echo ",waiting" >> $joblist
	    fi
	done
	#submit job, with next jobs tethered via PBS afterok
	bash $tether $joblist $template
	#this is equivalent to ./case.submit of $firstcase 
	#with a bit extra to automatically submit any tethered cases
    fi



done<$paramList
