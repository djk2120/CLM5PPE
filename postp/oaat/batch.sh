while read k; do
    sed 's/key/'$k'/g' casper.template > $k".job"
    qsub $k".job"

done<keys.txt
