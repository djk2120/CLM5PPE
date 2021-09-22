#!/bin/bash

#takes three arguments on the command-line
# e.g. bash collect.sh PPEn11/configs/CTL2010_s1.config h0 1
# 1 - config file
# 2 - history tape, e.g. h0, h1, ... , r
# 3 - whether to move files, 
#        0=don't move, just verify existence
#        1=move, but don't overwrite
#        2=move with overwrite


if [ $# -lt 3 ]
then
    echo "ERROR: please specify format file, htape, and whether to move files"
    echo "   ex: ./collect.sh spinAD.config h1 0"
    exit 1
fi

#set up environment variables
source $1
echo $1
jobdir=$(pwd)"/"
tape=$2
moveFiles=$3
fails=$(basename $1 .config)"_"$tape"_fails.txt"
> $fails


if [ $tape == 'r' ]; then
    NEW_DIR=$RESTARTS
else
    NEW_DIR=$HIST_DIR
fi

#loop through paramlist
while read p; do
    thiscase=$casePrefix"_"$p
    file=$SCRATCH$thiscase"/run/*.clm2."$tape".*nc"
    if [ ! -f $file ]; then
	echo $p" MAY HAVE FAILED"
	echo $p>>$fails
    else
	echo $p
	newfile=$NEW_DIR$(basename $file)
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
		mv $file $newfile
	    fi
	fi 
    fi
done < $paramList

nf=$(wc -l < $fails)
if [ $nf == 0 ]; then
    echo "All simulations yield "$tape" files"
    rm $fails
else
    echo "ERROR: one or more simulations may have crashed!"
    echo "       see "$fails
fi
