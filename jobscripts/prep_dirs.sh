codebase='PPEn11'
envtypes=('CTL2010' 'C285' 'AF1905')
runtypes=('hist_AD' 'hist_SASU' 'hist_postSASU' 'hist')
ensname='PPEn11'


basedir="/glade/scratch/djk2120/"


mkdir -p $basedir$ensname
mkdir -p $basedir$ensname"/restarts"

for envtype in ${envtypes[@]}; do
    for runtype in ${runtypes[@]}; do
	mkdir -p $basedir$ensname"/"$runtype"/"$envtype
    done
done

