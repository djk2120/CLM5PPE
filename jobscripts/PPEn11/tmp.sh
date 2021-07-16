for i in $(seq -f "%04g" 400 420); do
    echo 'OAAT'$i >> 'surv_resubmits.txt'
done
