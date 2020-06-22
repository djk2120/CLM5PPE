SCRIPTS_DIR="/glade/work/djk2120/ctsm_hardcode_co/cime/scripts/"
PARAMS_DIR=$(realpath ../params/paramfiles)"/"
NLMODS_DIR=$(realpath ../params/namelist_mods)"/"
RESTARTS="/glade/scratch/djk2120/mini_ens/"
basecase="clm50c6_ctsmhardcodep_2deg_GSWP3V1_Sparse250_2000pAD"
thisdir=$(pwd)
repcase="spinPostAD_001"
ninst=13



if [ 1 -eq 1 ]
then
cd $SCRIPTS_DIR
./create_clone --case $repcase --clone $basecase
cd $repcase
./xmlchange NINST_LND=$ninst
./xmlchange NTASKS_LND=1600
./case.setup --reset
fi


#loop through the paramfiles
#   creating a user_nl_clm_00xx for each
cd $PARAMS_DIR
CT=0
for path in spun/*.nc
do
    CT=$((CT+1))

    # locate and prepare mods to user_nl_clm
    f="$(basename -- $path)"
    printf -v nlnum "%04d" $CT
    nlfile="user_nl_clm_"$nlnum
    pfile=$PARAMS_DIR"spuntwice/"$f
    pfilestr="paramfile = '"$pfile"'"
    nlmods=$NLMODS_DIR${f%.*}".txt"
    rfile=$RESTARTS${f%.*}"_ADrestart.nc"
    rfilestr="finidat ='"$rfile"'"

    # copy and edit user_nl_clm
    cd $SCRIPTS_DIR$repcase
    cp user_nl_clm.base $nlfile
    echo $pfilestr >> $nlfile
    echo $rfilestr >> $nlfile
    cat $nlmods >> $nlfile

    # create a key to map each instance number to its paramfile
    printf $nlnum"\t"${f%.*}"\n" >> $repcase"_key.txt"


done

#move the paramfiles from "spinme" to "spun"
cd $PARAMS_DIR
for path in spun/*.nc
do
    mv $path spuntwice/
done


