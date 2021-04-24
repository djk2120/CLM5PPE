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
    echo "histdir="$histDir
    exit 1
fi

file_error=0
cd $SCRIPTS_DIR$ensname"/"$casePrefix
for p in $(ls); do  #loop through cases
    cd $p
    keyfile=$p"_key.txt"
    d=$SCRATCH$p"/run/"
    while read -r line; do #loop through instances
	tmp=(${line///}) 
	instkey=${tmp[0]}
	paramkey=${tmp[1]}

       	oldfile=$d$p".clm2_"$instkey"."$TAPE"."*
	oldfile=$(echo $oldfile)  #force wildcard expansion

	yrs="$(cut -d'.' -f4 <<<$oldfile)" #years is the fourth element if you split on '.'
	newfile=$histDir$histBase$paramkey$histSuffix$TAPE"."$yrs".nc"
	
	if [ -f $newfile ]; then
	    file_error=1
	    echo "ERROR: don't want to overwrite file"
	    echo " .... case="$p
	    echo " .... inst="$instkey
	    echo " .... paramkey="$paramkey
	    echo " .... file="$newfile
	else
	    echo "copying: "$paramkey
	    cp $oldfile $newfile
	fi


    done < $keyfile
    cd ..
done
if [ $file_error -eq 1 ]; then
    echo "One or more files not copied! See above..."
fi
