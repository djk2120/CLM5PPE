

JOB_ID=$1
prevcase=$2
repcase=$3

nextjob=$repcase".sh"

cat tether_part1.txt > $nextjob

echo "#PBS -W depend=afterok:"$JOB_ID >> $nextjob
echo "" >> $nextjob

echo 'prevcase="'$prevcase'"' >> $nextjob
echo 'repcase="'$repcase'"' >> $nextjob

cat tether_part2.txt >> $nextjob
echo "bash presubmit.sh $JOB_ID $repcase $nextcase "
