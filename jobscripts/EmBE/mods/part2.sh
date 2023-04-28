#!/bin/bash
prevcase=$1 
CASENAME=$(basename $2)
scratch='/glade/scratch/linnia/'

#########################################################################################
# PART 4
#########################################################################################
#
#    This script adds a few more history fields
#    and then runs the model for 1985-2004 as a branch run to get daily output
#
#########################################################################################


# --- Ensure that the env_run.xml file has the correct content
./xmlchange RUN_TYPE=branch
./xmlchange RUN_REFCASE=$CASENAME
./xmlchange RUN_REFDATE=1985-01-01
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=20
./xmlchange CONTINUE_RUN=FALSE
./xmlchange RESUBMIT=0



# start from original file if available
cp original_user_nl_clm user_nl_clm


# --- Add in the 'medium' history output items
echo -e "\n">> user_nl_clm
cat user_nl_clm_hist2 >> user_nl_clm
