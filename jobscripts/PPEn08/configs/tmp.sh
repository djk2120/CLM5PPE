file="/glade/u/home/djk2120/clm5ppe/jobscripts/PPEn08/configs/CTL2010_PROD_casekeys.txt"
for i in $(seq -f "%03g" 1 53); do
    echo $i >> $file
done
