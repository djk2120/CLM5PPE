#!/bin/bash
prevcase=$1 
scratch=$2 
CASENAME=$(basename $3)

##################################################################
# PART 1
#########################################################################################
#
#    This script sets up the rest of the low output portion of the simulation
#    1901-1984
#
#########################################################################################

WDIR=$scratch$CASENAME'/run/'
DDIR=$WDIR'restart_dump/'
mkdir -p $DDIR

mv $WDIR$CASENAME.datm.rs1*.bin $DDIR
gzip $DDIR$CASENAME*.bin


./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=84
./xmlchange DATM_CLMNCEP_YR_ALIGN=1901
./xmlchange DATM_CLMNCEP_YR_START=1901
./xmlchange DATM_CLMNCEP_YR_END=2014
./xmlchange CONTINUE_RUN=TRUE


# need to use user_nl_datm files to get years right
cp user_nl_datm1901-2014 user_nl_datm
