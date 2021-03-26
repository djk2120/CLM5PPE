if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./collect_runs.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"


if [ ! -d $histDir ]
then
    echo "create history dir"
fi
cd $SCRIPTS_DIR$casePrefix
for p in $(ls); do  #loop through cases
    cd $p
    keyfile=$p"_key.txt"
    d=$SCRATCH$p"/run/"
    while read -r line; do #loop through instances
	tmp=(${line///}) 
	paramkey=${tmp[0]}
	matchme=$d$p".clm2."$TAPE".*"
	oldfiles=$(ls $matchme)
	for oldfile in $oldfiles; do #loop through history files
	    yrs="$(cut -d'.' -f4 <<<$oldfile)" #years is the fourth element if you split on '.'
	    newfile=$histDir$histBase$paramkey$histSuffix$TAPE"."$yrs".nc"
	    echo "cp "$oldfile" "$newfile
	    cp $oldfile $newfile  #the end result!
	done
    done < $keyfile
    cd ..
done
