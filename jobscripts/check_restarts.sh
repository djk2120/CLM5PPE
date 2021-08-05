if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./runens.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"
moveFiles=$2

file_name="${paramList##*/}"
chunk="${file_name%.*}"
rejects=$codebase"/"$casePrefix"_"$chunk"_rejects.txt"


#loop through paramlist
failedrun=0
while read p; do
    repcase=$casePrefix"_"$p
    rfile=$SCRATCH$repcase"/run/*.clm2.r.*"
    newfile=$RESTARTS$(basename $rfile)


    if [ ! -f $rfile ]; then
	echo $p" MAY HAVE FAILED"
	failedrun=1
	echo $p >> $rejects
    fi

    if [ $moveFiles -gt 0 ]; then 
	already=0
	if [ -f $newfile ]; then
	    already=1
	    
	    if [ $moveFiles -eq 1 ]; then
		echo $p" restart already exists, will not copy"
	    else
		echo $p" restart already exists, file overwritten"
	    fi
	fi
	if [ $already == 0 ] || [ $2 == 2 ]; then
	    cp $rfile $newfile
	fi
    fi 


done <$paramList


if [ $failedrun == 1 ]; then
    echo "ERROR: one or more simulations may have crashed!"
else
    echo "All simulations yield restart files"
fi
