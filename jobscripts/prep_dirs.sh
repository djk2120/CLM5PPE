codebase='PPEn11'
envtypes=('CTL2010' 'C285' 'AF1905')
runtypes=('hist_AD' 'hist_SASU' 'hist_postSASU' 'hist')



basedir="/glade/scratch/djk2120/"


for envtype in ${envtypes[@]}; do
    for runtype in ${runtypes[@]}; do
	mkdir -p $basedir$codebase"/"$runtype"/"$envtype
    done
done

