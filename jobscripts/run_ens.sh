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
joblist='tethered.txt' 

#create and submit all the cases
while read p; do  #loop through paramfiles
    for i in "${!cases[@]}"; do  #loop through spinup stages
	case="${cases[i]}"
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

	#set up job tethering
	if (( i == 0 )); then
	    firstcase=$thiscase
	    :> $joblist  #empty file
	else
	    cd $firstcase
	    echo $thiscase >> $joblist
	fi
    done

    #submit job, with next jobs tethered via PBS afterok
    cd $PPE
    prevcase="none"
    bash tether.sh $prevcase $SCRATCH $firstcase $joblist $template
    #this is equivalent to ./case.submit of $firstcase 
    #plus a bit extra to automatically submit any tethered cases

done<$paramList
