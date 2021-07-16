p='OAAT0005'


d1='/glade/scratch/djk2120/PPEn11/hist/CTL2010/'
d2='/glade/scratch/djk2120/PPEn11/hist/C285/'

i=0
for f in $(ls $d2); do
    A="$(cut -d'_' -f3 <<<$f)"
    B="$(cut -d'.' -f1 <<<$A)"
    H="$(cut -d'.' -f3 <<<$f)"
    
    if compgen -G $d1"*"$B"*."$H".*" > /dev/null; then
	x=1
    else
	echo $B"-"$H"not here"
    fi
	
done




