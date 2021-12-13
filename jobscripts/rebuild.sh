envtypes=('CTL2010' 'C285' 'AF1855' 'C867' 'NDEP' 'AF2095')




s='/glade/work/djk2120/PPEn11/cime/scripts'
cd $s
for envtype in ${envtypes[@]}; do
    cd $envtype"/basecases"

#    cd "PPEn11_"$envtype"_AD"
#    pwd
#    ./case.build --clean-all                                                                                                       
#    ./case.build 

    
    for d in $(ls); do
	echo $d
	cd $d
	./case.build --clean-all
	./case.build
	cd -
    done
    
    cd $s
done
