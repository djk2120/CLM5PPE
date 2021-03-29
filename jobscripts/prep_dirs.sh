codebase='PPEn08'
envtypes=('I2000' 'C285' 'C867' 'W1905' 'W2095' 'ndepp5')
runtypes=('AD' 'SASU' 'postSASU' 'PROD')
ensname='test34'


basedir="/glade/scratch/djk2120/clm5ppe/"


mkdir -p $basedir$ensname
mkdir -p $basedir$ensname"/restarts"

for envtype in ${envtypes[@]}; do
    mkdir -p $basedir$ensname"/"$envtype
    for runtype in ${runtypes[@]}; do
	mkdir -p $basedir$ensname"/"$envtype"/hist"$runtype
    done
done

