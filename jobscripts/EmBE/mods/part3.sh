#!/bin/bash
prevcase=$1 
CASENAME=$(basename $2)
scratch='/glade/scratch/linnia/'

#########################################################################################
# PART 5
#########################################################################################
#
#    This script adds some various history fields
#    and then runs the model for 2005-2014 as a branch run to get daily and subdaily output
#
#########################################################################################

# --- Ensure that the env_run.xml file has the correct content
./xmlchange RUN_TYPE=branch
./xmlchange RUN_REFCASE=$CASENAME
./xmlchange RUN_REFDATE=2005-01-01
./xmlchange STOP_OPTION=nyears
./xmlchange STOP_N=10
./xmlchange CONTINUE_RUN=FALSE
./xmlchange RESUBMIT=0

# --- Add in the subdaily output streams
# --- Reset the user namelist file.
cp original_user_nl_clm user_nl_clm

# --- Add in the subdaily history output items
echo -e "\n">> user_nl_clm
cat user_nl_clm_hist3 >> user_nl_clm
