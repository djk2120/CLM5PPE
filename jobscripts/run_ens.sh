if [ $# -lt 1 ]
then
    echo "ERROR: please specify config file"
    echo "   ex: ./runens.sh AF1855_AD_e0.config"
    exit 1
fi

#set up environment variables
source $1


while read p; do

    for case in ${cases[@]}; do
	basecase=$SCRIPTS$ensemble"/basecases/"$case
	thiscase=$SCRIPTS$ensemble"/"$case"/"$case"_"$p
	
	#clone case
	cd $SCRIPTS
	./create_clone --case $thiscase --clone $basecase
	
	#setup, point to executable
	cd $thiscase
	./case.setup
	./xmlchange BUILD_COMPLETE=TRUE
	./xmlchange EXEROOT=$SCRATCH$case"/bld"
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
	
    done

    #set up job tethering
    i=0
    joblist='tethered.txt'
    for case in ${cases[@]}; do
        i=$((i+1))
	thiscase=$SCRIPTS$ensemble"/"$case"/"$case"_"$p
	if (( i ==1 )); then
	    cd $thiscase
	    firstcase=$thiscase
	    :> $joblist  #empty file
	else
	    echo $thiscase >> $joblist
	fi
    done

    #submit job, with next jobs tethered via PBS afterok
    cd $PPE
    prevcase="none"
    bash tether.sh $prevcase $SCRATCH $firstcase $joblist $template

done<$paramList
