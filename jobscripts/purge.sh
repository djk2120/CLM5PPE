#CUIDADO

paramlist=$1

envtypes=('CTL2010' 'C285' 'AF1855' 'C867' 'NDEP' 'AF2095')
s='/glade/work/djk2120/PPEn11/cime/scripts/'
scra='/glade/scratch/djk2120/'

for envtype in ${envtypes[@]}; do
    cd $s
    cd $envtype
    for d in $(ls); do
	cd $d
	while read p; do
	    for d in "*"$p"*"; do
		if [ -d $d ]; then
		    rm -r $d
		    rm -r $scra$d
		fi
	    done
	done < $paramlist
	cd $s$envtype
    done
done
