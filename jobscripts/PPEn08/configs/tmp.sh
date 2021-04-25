file="/glade/u/home/djk2120/clm5ppe/jobscripts/PPEn08/configs/CTL2010_SASU_rejects_casekeys.txt"
for i in $(seq -f "%03g" 56 76); do
    echo $i >> $file
done
