prevcase=$1
scratch=$2
thiscase=$3
joblist=$4
template=$5

cd $thiscase



#handle finidat
if [ $prevcase != 'none' ]; then
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

    #find the appropirate restart file
    casename=${prevcase##*/}
    restart=$scratch$casename'/run/'$casename".clm2.r."*".nc"
    restart=$(echo $restart) #expands wildcard

    #append to user_nl_clm
    echo -e 'finidat="'$restart'"'>>user_nl_clm
fi

#submit case, capturing JOB_ID
./case.submit > submit_out
JOB_ID=$(grep "Submitted job id is" submit_out | tail -1 | cut -f 5 -d' ')

#presubmit next case, if any are left
njobs=$(wc -l < $joblist)
if (( $njobs > 0 ));then 
    #read next job from joblist
    nextcase=$(head -n 1 $joblist)
    echo "nextcase="$nextcase

    #cp joblist to nextcase, removing nextcase
    tail -n +2 $joblist > file.tmp 
    mv file.tmp $nextcase'/'$joblist
    
    #prepare the next job submission
    casename=${nextcase##*/}
    nextjob=$nextcase"/"$casename".presubmission"
    cp $template $nextjob

    sed -i -e 's:JOB_ID:'$JOB_ID':g' $nextjob
    sed -i -e 's:jobname:pre_'$casename':g' $nextjob
    sed -i -e 's:prevcase:'$thiscase':g' $nextjob
    sed -i -e 's:scratch:'$scratch':g' $nextjob
    sed -i -e 's:thiscase:'$nextcase':g' $nextjob
    sed -i -e 's:joblist:'$joblist':g' $nextjob
    sed -i -e 's:template:'$template':g' $nextjob

    #presubmit the next job
    qsub $nextjob


fi
