envtypes=('CTL2010' 'C285' 'AF1855' 'C867' 'NDEP' 'AF2095')
suffs=('_AD' '_SASU' '_postSASU' '/')
s="/glade/work/djk2120/PPEn11/cime/scripts/"
cb="PPEn11"

PWD=$(pwd)
f=$PWD"/rebuilt.txt"
:>$f

for suff in ${suffs[@]}; do
    for envtype in ${envtypes[@]}; do
	d=$s$envtype"/basecases/"
	c=$d$cb"_"$envtype$suff
	echo $c >> $f
	cd $c
	./case.build
    done
done
