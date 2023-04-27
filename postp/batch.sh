mv OAAT_surv.nc OAAT_surv.old

while read exp; do
    sed 's/CTL2010/'$exp'/g' crunch/template.sh > 'crunch/'$exp'.sh'
    jobid=$(qsub 'crunch/'$exp'.sh')
done <exps.txt
sed 's/jobid/'$jobid'/g' enscat.sh > enscat_tmp.sh
qsub enscat_tmp.sh
