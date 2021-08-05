#DONT forget to run the simulations to generate a finidat



cd /glade/work/djk2120/PPEn11/cime/scripts

env='AF1855'

KEITHDIR='/glade/work/oleson/PPE.n08_ctsm5.1.dev023/cime/scripts/'

clonecases=('ctsm51c6_PPEn08ctsm51d023_2deg_GSWP3V1_Sparse400_PI-1850-1859_2000AD' \
    'ctsm51c6_PPEn08ctsm51d023_2deg_GSWP3V1_Sparse400_PI-1850-1859_step3' \
    'ctsm51c6_PPEn08ctsm51d023_2deg_GSWP3V1_Sparse400_PI-1850-1859_step4' \
    'ctsm51c6_PPEn08ctsm51d023_2deg_GSWP3V1_Sparse400_PI-1850-1859_2000')

newsuffs=('_AD' '_SASU' '_postSASU' '')

mkdir -p $env"/basecases"

for (( i=0; i<4; i++ ));
do

    clonecase=$KEITHDIR${clonecases[$i]}
    suff=${newsuffs[$i]}
    newcase=$env"/basecases/PPEn11_"$env$suff

    ./create_clone --clone $clonecase --case $newcase --cime-output-root /glade/scratch/djk2120
    
    cd $newcase
    ./case.setup
    ./xmlchange DOUT_S="false"
    ./xmlchange JOB_QUEUE="economy"
    ./xmlchange PROJECT="P08010000"
    ./case.build

    cd -

done




