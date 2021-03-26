if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./runens.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"

#count existing cases
# so that we give this case a new name
cd $SCRIPTS_DIR
if [ -d $casePrefix ]
then
    j=$(ls $casePrefix | wc -w)
else j=0
fi
cd $jobdir

# custom function to read n lines from a file
read_n() { for i in $(seq $1); do read || return; echo $REPLY; done; }

# count how many parameter sets in this batch
nx=$(wc -l < $paramList)
ninst0=$ninst

# outer loop creates a new multi-instance case
i=0
while [ $i -lt $nx ]
do
    nl=$((nx-i)) #how many more paramsets?
    if [ $nl -lt $ninst ]
    then         #adjust ninst if there's an odd remainder
	ninst=$nl
	exerootFlag=false  #must rebuild
    fi

    i=$((i+ninst))
    j=$((j+1))

    #create the new case 
    repcase=$casePrefix"_"$(seq -f "%03g" $j $j)
    echo "--------------------------"
    echo "   creating "$repcase
    echo "--------------------------"
    cd $SCRIPTS_DIR
    ./create_clone --case $casePrefix"/"$repcase --clone $basecase
    cd $casePrefix"/"$repcase

    #adjust ninst if needed
    if [ $ninst -ne $ninst0 ]; then
	./xmlchange NINST_LND=$ninst
    fi

    #setup and point to executable
    ./case.setup --reset
    if [ "$exerootFlag" = true ]
    then
	./xmlchange BUILD_COMPLETE=TRUE
	./xmlchange EXEROOT=$exeroot
    fi

    #inner loop sets up each instance
    #   creating a user_nl_clm_00xx for each paramset
    CT=0
    extraline="\!"
    lines="$(read_n $ninst)"
    for p in $lines; do 
	CT=$((CT+1))
	printf -v nlnum "%04d" $CT

	if [ $ninst -gt 1 ]; then
	    nlfile="user_nl_clm_"$nlnum
	else
	    nlfile="user_nl_clm"
	fi
	pfile=$PARAMS_DIR$p".nc"
	pfilestr="paramfile = '"$pfile"'"
	

	# copy user_nl_clm and specify paramfile
	cd $SCRIPTS_DIR$casePrefix"/"$repcase
	cp user_nl_clm.base $nlfile
	echo -e "\n"$pfilestr >> $nlfile

	# specify finidat if needed
	if [ "$finidatFlag" = true ]
	then
	    rfile=$RESTARTS$p$finidatSuff
	    rfilestr="finidat ='"$rfile"'"
	    echo $rfilestr >> $nlfile
	fi

	# cat nlmods if needed
	if [ "$nlmodsFlag" = true ]
	then
	    nlmods=$NLMODS_DIR$p".txt"
	    cat $nlmods >> $nlfile
	fi
		
	# create a key to map each instance number to its paramfile
	printf $nlnum"\t"$p"\n" >> $repcase"_key.txt"

	
    done	

    # build case, if need be
    if [ "$exerootFlag" = false ]; then
	echo "--------------------------"
	echo "   building "$repcase
	echo "--------------------------"
	./case.build
	#only need to compile the source code once
	exeroot=$SCRATCH$repcase"/bld"
	exerootFlag=true
    fi
    
    # submit
    echo "--------------------------"
    echo "   submitting "$repcase
    echo "--------------------------"
    ./case.submit
    
    

done < $jobdir$paramList
    
