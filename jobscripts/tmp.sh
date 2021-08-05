cd /glade/work/djk2120/PPEn11/cime/scripts/AF1855/PPEn11_AF1855_postSASU/
scratch='/glade/scratch/djk2120/'


for c in $(ls /glade/work/djk2120/PPEn11/cime/scripts/AF1855/PPEn11_AF1855_postSASU/);do 
    rf=$scratch$c"/run/*.clm2.r.*.nc"
    rf=$(echo $rf)
    if [ ! -f $rf ];then 
	echo $c
	cd $c
	./xmlchange JOB_QUEUE="regular"
	./case.submit
	cd -
    fi
done
