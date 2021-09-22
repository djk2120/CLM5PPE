
# a very brittle script to automatically populate config file


ensname=$1
runtype=$2
chunk=$3

codebase='PPEn11'
PPE_DIR="/glade/u/home/djk2120/clm5ppe/jobscripts/"
SCRATCH="/glade/scratch/djk2120/"

#create pad
if [ $runtype == 'PROD' ];then
    runtype=''
    pad=''
else
    pad='_'
fi

#establish the config file
config=$codebase"/configs/"$ensname$pad$runtype"_"$chunk".config"
echo "#CONFIG file for: "$ensname$pad$runtype"_"$chunk > $config
echo "" >> $config

#VARIOUS DIR LOCATIONS
x='#need to identify where the script can expect certain files'
echo $x >> $config

x='PPE_DIR="'$PPE_DIR'"'
echo $x >> $config
x='SCRIPTS_DIR="/glade/work/djk2120/'$codebase'/cime/scripts/"'
echo $x >> $config
x='SCRATCH="'$SCRATCH'"'
echo $x >> $config
x='RESTARTS="'$SCRATCH$codebase'/restarts/"'
echo $x >> $config
x='HIST_DIR="'$SCRATCH$codebase'/hist'$pad$runtype'/'$ensname'/"'
echo $x >> $config

#CASEPREFIX
echo "" >> $config
x='#prefix to identify these cases '
echo $x >> $config
casePrefix=$codebase"_"$ensname$pad$runtype
x='casePrefix="'$casePrefix'"'
echo $x >> $config
caseDir=$ensname"/"$casePrefix"/"
x='caseDir="'$caseDir'"'
echo $x >> $config

#BASECASE
echo "" >> $config
x='#the case that will be cloned to create the ensemble'
echo $x >> $config
x='basecase="'$ensname'/basecases/'$codebase"_"$ensname$pad$runtype'"'
echo $x >> $config

#PARAMLIST
echo "" >> $config
x='#the list of paramfiles '
echo $x >> $config
x='paramList="'$codebase'/'$chunk'.txt"'
echo $x >> $config


#ESTABLISH PREVIOUS CASE
if [[ $runtype == "SASU" ]];then
    prevtype="AD"
elif [[ $runtype == "postSASU" ]];then
    prevtype="SASU"
else
    prevtype="postSASU"
fi

#FINIDAT
echo "" >> $config
x='#options for specifying unique restart files for each paramset'
echo $x >> $config
if [[ $runtype == "AD" ]];then 
    x='finidatFlag=false'
    echo $x >> $config
else
    x='finidatFlag=true'
    echo $x >> $config
    prevCase=$codebase"_"$ensname"_"$prevtype
    x='prevCase="'$prevCase'"'
    echo $x >> $config
fi


#PARAMLOC
echo "" >> $config
x='#where to find the parameter files'
echo $x >> $config
x='PARAMS_DIR="'$SCRATCH$codebase'/paramfiles/"'
echo $x >> $config

#NLMODS
echo "" >> $config
x='#options for specify unique namelist_mods for each paramset'
echo $x >> $config
x='#   e.g. if you are varying baseflow_scalar'
echo $x >> $config
x='nlmodsFlag=true'
echo $x >> $config
x='nlbase="'$PPE_DIR$codebase"/nlbase/"$ensname"/"$ensname$pad$runtype'.base"'
echo $x >> $config
x='NLMODS_DIR="'$SCRATCH$codebase'/namelist_mods/"'
echo $x >> $config


#EXEROOT
echo "" >> $config
x='#options for specifying a previous build'
echo $x >> $config
x='#   note that this exeroot much use the same ninst'
echo $x >> $config
x='exerootFlag=true'
echo $x >> $config
x='exeroot="'$SCRATCH$codebase"_"$ensname$pad$runtype'/bld"'
echo $x >> $config
