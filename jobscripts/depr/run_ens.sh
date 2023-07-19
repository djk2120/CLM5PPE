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

#create and submit all the cases
while read p; do  #loop through paramfiles

    echo "CLONING CASES"

    for i in "${!stages[@]}"; do  #loop through spinup stages
	case="${stages[i]}"
	exeroot="${exeroots[i]}"

	basecase=$SCRIPTS$ensemble"/basecases/"$case
	thiscase=$SCRIPTS$ensemble"/"$case"/"$case"_"$p
	
	#clone case
	cd $SCRIPTS
	./create_clone --case $thiscase --clone $basecase
	
	#setup, point to executable
	cd $thiscase
	./case.setup
	./xmlchange BUILD_COMPLETE=TRUE
	./xmlchange EXEROOT=$exeroot
	./xmlchange DOUT_S=FALSE
	./xmlchange PROJECT=$PROJECT
	#./xmlchange JOB_QUEUE="regular"

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
    done

    #tethering setup
    case="${cases[0]}"
    firstcase=$SCRIPTS$ensemble"/"$case"/"$case"_"$p
    cd $firstcase
    :> $joblist
    for i in "${!cases[@]}"; do  #loop through all steps/substeps
	case="${cases[i]}"
	casemod="${casemods[i]}"
	thiscase=$SCRIPTS$ensemble"/"$case"/"$case"_"$p
	
	echo -n $case"_"$p >> $joblist
	echo -n ","$thiscase >> $joblist
	echo -n ","$casemod >> $joblist

	if [ $i -eq 0 ]; then
	    echo ",queued" >> $joblist
	else
	    echo ",waiting" >> $joblist
	fi

    done

    # #submit job, with next jobs tethered via PBS afterok
    bash $tether $joblist $template
    # #this is equivalent to ./case.submit of $firstcase 
    # #plus a bit extra to automatically submit any tethered cases

done<$paramList
