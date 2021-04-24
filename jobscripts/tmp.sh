if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./runens.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"

rejects=$jobdir$codebase"/"$ensname"_"$runtype"_rejects.txt"
echo $rejects

#collect restarts
failedrun=0

for p in $(ls); do
    cd $p
    keyfile=$p"_key.txt"
    d=$SCRATCH$p"/run/"
    while read -r line; do 
	tmp=(${line///}) 
	paramkey=${tmp[1]} 
	instkey=${tmp[0]}

	if [ $ninst -gt 1 ]; then
	    inst="_"$instkey
	fi

	oldfile=$d$p".clm2"$inst".r.*"
	newfile=$RESTARTS$ensname"_"$paramkey$finidatSuff

	if [ -f $oldfile ]; then
	    x=1
	    #echo "cp "$oldfile" "$newfile
	    #cp $oldfile $newfile
	else
	    failedrun=1
	    #echo "!!! File not found: "$oldfile
	    echo $paramkey
	    echo $paramkey >> $rejects
	fi

    done < $keyfile
    cd ..
done

if [ $failedrun -eq 1 ]; then
    echo "---------------------------------------------------------------------------"
    echo "One or more simulations may have crashed! Check restarts before continuing."
    echo "---------------------------------------------------------------------------"
fi
