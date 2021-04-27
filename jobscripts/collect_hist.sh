if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./collect_hist.sh ppe.config"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"

runtypes=('AD' 'SASU' 'postSASU' 'PROD')



runtype='PROD'

if [ $runtype = "PROD" ]; then
    rstr=""
else
    rstr="_"$runtype
fi


newdir=$SCRATCH$codebase"/"$ensname"/hist"$rstr"/"
if [ ! -d $newdir ]; then
    mkdir $newdir
fi

cd $SCRIPTS_DIR$ensname"/"$codebase"_"$ensname"_"$runtype
#cases=("PPEn08_CTL2010_postSASU_002") ${cases[@]}; do
for case in $(ls);do
    cd $SCRIPTS_DIR$ensname"/"$codebase"_"$ensname"_"$runtype
    cd $case
    ninst=$(./xmlquery NINST_LND | cut -d':' -f2)
    
    keyfile=$case"_key.txt"
    while read -r line; do
	tmp=(${line///}) 
	paramkey=${tmp[1]} 
	instkey=${tmp[0]}
	
	if [ $ninst -gt 1 ]; then
	    inst="_"$instkey
	else
	    inst=""
	fi
	
	rfile=$SCRATCH$case"/run/"$case".clm2"$inst".r.*"
	if [ -f $rfile ]; then
	    echo $paramkey
	    for i in $(seq 0 7); do
		hfile=$SCRATCH$case"/run/"$case".clm2"$inst".h"$i".*"
		hfile=$(echo $hfile)  #force wildcard expansion
		if [ -f $hfile ]; then
		    yrs="$(cut -d'.' -f4 <<<$hfile)" #years is the fourth element if you split on '.'
		    ff=$codebase"_"$ensname$rstr"_"$paramkey".clm2.h"$i"."$yrs".nc"
		    newfile=$newdir$ff
		    if [ -f $newfile ]; then
			echo "ABORT MV: "$ff"already exists"
		    else
			#echo "mv "$hfile" "$newfile
			mv $hfile $newfile
		    fi
		fi
	    done
	else
	    echo "ERROR: no restartfile, "$paramkey
	fi
		
    done < $keyfile
done





