#!/bin/bash
if [ $# -lt 1 ]
then
    echo "ERROR: please specify config file"
    echo "   ex: ./runens.sh CTL2010_chunk1.config"
    exit 1
fi

#set up environment variables
source $1

top="/glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/"$ensemble"/"
mkdir -p $top"hist"
mkdir -p $top"spin"
mkdir -p $top"rest"


needdepr=1
while read p; do
    for basecase in ${cases[@]}; do
	c=$(basename $basecase)
	
	case=$c"_"$p
	suff=$(echo $case | cut -d_ -f3)
	skip=0
	if [ $suff = 'postSASU' ]; then
	    NEWDIRS=( $top"spin/" $top"rest/" )
	    matches=( "clm2.h" "clm2.r." )
	elif [ $suff = $p ]; then
	    NEWDIRS=( $top"hist/" )
	    matches=( "clm2.h" )
	else
	    skip=1
	fi
	if [[ $skip < 1 ]]; then
	    echo $case
	    cd $SCRATCH
	    cd $case"/run/"
	    for i in ${!matches[@]}; do
		match=${matches[$i]}
		NEWDIR=${NEWDIRS[$i]}
	
		for file in *$match*; do
		    f2=$NEWDIR$file
		    if [ -f $f2 ]; then
			if [[ $needdepr -eq 1 ]]; then
			    dd=$(date +%Y%m%d)
			    depr=$top"depr/c"$dd"/"
			    mkdir -p $depr
			    needdepr=0
			fi
			mv $f2 $depr
		    fi    
		    
		    mv $file $NEWDIR
		done
	    done
	fi
    done
done <$paramList


if [[ $needdepr -eq 0 ]]; 
    echo "Some files were deprecated!"
    echo "  see: "$depr
fi




