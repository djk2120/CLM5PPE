envtypes=('CTL2010' 'C285' 'AF1855')

paramlist='/glade/u/home/djk2120/clm5ppe/jobscripts/PPEn11/s2.txt'


s='/glade/work/djk2120/PPEn11/cime/scripts'
cd $s
for envtype in ${envtypes[@]}; do
    cd $envtype"/basecases"
    for d in $(ls); do
	echo $d
	cd $d
	./case.build --clean-all
	./case.build
	cd -
    done
    
    cd $s
done
