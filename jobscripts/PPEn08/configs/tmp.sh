file="/glade/u/home/djk2120/clm5ppe/jobscripts/PPEn08/configs/CTL2010_SASU_casekeys.txt"
for i in $(seq -f "%03g" 1 55); do
    echo $i >> $file
done
