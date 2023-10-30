#!/bin/bash
if [ $# -lt 1 ]
then
    echo "ERROR: please specify config file"
    echo "   ex: ./runens.sh CTL2010_chunk1.config"
    exit 1
fi

#set up environment variables
source $1

while read p; do
    for basecase in ${cases[@]}; do
	case=$(basename $basecase)
	echo $case"_"$p
    done
done <$paramList

echo "The preceding cases will all be deleted!!!!"
echo "   INCLUDING OUTPUT!!"

read -p ' proceed? (y/n): ' proceed

if [ $proceed = "y" ]; then
    echo "...15 seconds to abort (ctrl-z)..."
    sleep 15
    while read p; do
	for basecase in ${cases[@]}; do
	    case=$(basename $basecase)
	    echo $case"_"$p


	    thiscase=$CASEDIR$case"/"$case"_"$p
	    rm -r $thiscase
    
    
	    cd $SCRATCH
	    rm -r $case"_"$p
	done
    done <$paramList
fi

