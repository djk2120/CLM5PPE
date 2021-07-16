if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./runens.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"



#loop through paramlist
failedrun=0
already=0
htapes=('h0' 'h1' 'h2' 'h3' 'h4' 'h5' 'h7')

pad=''
histdir=$SCRATCH$codebase"/hist"$pad$runtype"/"$ensname"/"

while read p; do
    echo $p
    for htape in "${htapes[@]}"; do
	repcase=$casePrefix"_"$p
	hfile=$SCRATCH$repcase"/run/*.clm2."$htape".*"
	newfile=$histdir$(basename $hfile)

	if [ ! -f $hfile ]; then
	    echo $p" MAY HAVE FAILED"
	    failedrun=1
	fi

	if [ -f $newfile ]; then
	    already=1
	    echo $newfile" ALREADY EXISTS, not copied"
	else
	    mv $hfile $newfile
	fi

    done
done <$paramList


if [ $failedrun == 1 ]; then
    echo "ERROR: one or more simulations may have crashed!"
else
    echo "All simulations yield restart files"
fi

if [ $already == 1 ]; then
    echo "ERROR: one or more simulations had already existed!"
else
    echo "All history files were moved"
fi

