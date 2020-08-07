#!/bin/bash
# Daniel Kennedy (djk2120@ucar.edu)

if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./runens.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"

#collect restarts if needed
if [ "$finidatFlag" = true ]
then
    if [ ! -d $RESTARTS ]
    then
	mkdir $RESTARTS
    fi
    cd $SCRIPTS_DIR$prevCase
    for p in $(ls); do
	cd $p
	keyfile=$p"_key.txt"
	d=$SCRATCH$p"/run/"
	while read -r line; do 
	    tmp=(${line///}) 
	    paramkey=${tmp[1]} 
	    instkey=${tmp[0]}
	    oldfile=$d$p".clm2_"$instkey".r.*"
	    newfile=$RESTARTS$paramkey$finidatSuff
	    echo "cp "$oldfile" "$newfile
	    cp $oldfile $newfile
	done < $keyfile
	cd ..
    done
fi

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

# outer loop creates a new multi-instance case
i=0
while [ $i -lt $nx ]
do
    nl=$((nx-i)) #how many more lines in the file?
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
    ./xmlchange NINST_LND=$ninst
    ./case.setup --reset
    if [ "$exerootFlag" = true ]
    then
	./xmlchange BUILD_COMPLETE=TRUE
	./xmlchange EXEROOT=$exeroot
    fi
    
    #inner loop sets up each instance
    #   creating a user_nl_clm_00xx for each paramset
    CT=0
    lines="$(read_n $ninst)"
    for p in $lines; do 
	CT=$((CT+1))

	printf -v nlnum "%04d" $CT
	nlfile="user_nl_clm_"$nlnum
	pfile=$PARAMS_DIR$p".nc"
	pfilestr="paramfile = '"$pfile"'"

	# copy user_nl_clm and specify paramfile
	cd $SCRIPTS_DIR$casePrefix"/"$repcase
	cp user_nl_clm.base $nlfile
	echo $pfilestr >> $nlfile

	# cat nlmods if needed
	if [ "$nlmodsFlag" = true ]
	then
	    nlmods=$NLMODS_DIR$p".txt"
	    cat $nlmods >> $nlfile
	fi

	# specify finidat if needed
	if [ "$finidatFlag" = true ]
	then
	    rfile=$RESTARTS$p$finidatSuff
	    rfilestr="finidat ='"$rfile"'"
	    echo $rfilestr >> $nlfile
	fi

	# create a key to map each instance number to its paramfile
	printf $nlnum"\t"$p"\n" >> $repcase"_key.txt"
    done

    if [ "$exerootFlag" = false ]; then
	echo "--------------------------"
	echo "   building "$repcase
	echo "--------------------------"
	./case.build
	#only need to compile the source code once
	exeroot=$SCRATCH$repcase"/bld"
	exerootFlag=true
    fi

    echo "--------------------------"
    echo "   submitting "$repcase
    echo "--------------------------"
    ./case.submit

done < $jobdir$paramList


