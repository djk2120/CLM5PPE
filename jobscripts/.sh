#!/bin/bash
#PBS -q premium
#PBS -l walltime=12:00:00
#PBS -A P93300641
#PBS -j oe
#PBS -k eod
#PBS -l select=1:ncpus=1
#PBS -W depend=afterok:testspin1

prevcase="testspin2"
repcase=""
SCRATCH="/glade/scratch/djk2120/"
SCRIPTS="/glade/work/djk2120/ctsm_medlyn/cime/scripts/"

#find the previous restart file
restart=$SCRATCH$prevcase"/run/"$prevcase".clm2.r."*".nc"
restart=$(echo $restart) #expands wildcard

#append to user_nl_clm
cd $SCRIPTS$repcase
echo -e 'finidat="'$restart'"'>>user_nl_clm

#submit case, capturing JOB_ID
./case.submit > submit_out
JOB_ID=$(grep "Submitted job id is" submit_out | tail -1 | cut -f 5 -d' ')
echo $JOB_ID

#presubmit next case, if any are left
cd -
njobs=$(wc -l < jobs_to_run.txt)
echo "njobs="$njobs
if (( $njobs > 0 ));then 
   nextcase=$(head -n 1 jobs_to_run.txt)
   tail -n +2 jobs_to_run.txt > file.tmp 
   mv file.tmp jobs_to_run.txt
   bash presubmit.sh $JOB_ID $repcase $nextcase  #this script prepares nextjob.sh
   nextjob="./"$nextcase".sh"
   qsub $nextjob
fi
