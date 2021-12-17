#!/bin/bash

#takes three arguments on the command-line
# e.g. bash collect.sh PPEn11/configs/CTL2010_s1.config h0 1
# 1 - config file
# 2 - whether to move files, 
#        0=don't move, just verify existence
#        1=move, but don't overwrite
#        2=move with overwrite


if [ $# -lt 2 ]
then
    echo "ERROR: please specify format file and whether to move files"
    echo "   ex: ./collect.sh spinAD.config 0"
    exit 1
fi



#set up environment variables
source $1
echo $1
jobdir=$(pwd)"/"
moveFiles=$2


tapes=('r' 'h0' 'h1' 'h2' 'h3' 'h4' 'h5' 'h7') 
for tape in ${tapes[@]};do

    fails=$(basename $1 .config)"_"$tape"_fails.txt"
    :> $fails
    echo "checking for "$tape" files"

    if [ $tape == 'r' ]; then
	NEW_DIR=$RESTARTS
    else
	NEW_DIR=$HIST_DIR
    fi
    if [ $moveFiles -gt 0 ]; then
	mkdir -p $NEW_DIR
	echo "collecting files in "$NEW_DIR
    fi

    #loop through paramlist
    while read p; do
	thiscase=${cases[-1]}"_"$p
	files=$SCRATCH$thiscase"/run/*.clm2."$tape".*nc"
	
	if compgen -G $files > /dev/null; then
	    i=0
	    for file in $files; do
		i=$((i+1))
		if [ $i == 1 ]; then
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
			if [ $already == 0 ] || [ $3 == 2 ]; then
			    mv $file $newfile
			fi
		    fi 
		fi
	    done
	else
	    echo $p" MAY HAVE FAILED"
	    echo $p>>$fails
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

done
