:>tmp.txt
rm *.txt
bash split_files.sh

for f in *.txt; do
    fname="${f%.*}"    
    job=$fname".job"
    sed 's/CTL2010/'$fname'/g' template.sh > $job
    sed -i 's/zqz/'$f'/g' $job
    #qsub $job
done


rm *.txt
