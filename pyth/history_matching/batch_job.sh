
for i in {001..100}; do
    
    sed 's/num/'$i'/g' template.sh > 'pxb_'$i'.job'
    qsub 'pxb_'$i'.job'

done


