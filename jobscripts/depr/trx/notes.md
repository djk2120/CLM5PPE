
### April 25, 2022

- writing a new basecase script to clone, build, and submit keith's simulations
- using a reworked version of tether.sh to submit together


### April 28, 2022
- needed to re-checkout CTSM to match Keith's cime
  - startup.sh
- cloning and building the four cases
  - basecases.sh

### May 4, 2022
- fixing up tether to not require modlist in the same dir
- need to point to new paramfile with the new source code
  - paramfile = '/glade/p/cgd/tss/people/oleson/modify_param/ctsm51_params.c210507_kwo.c220322.nc'
  - adding this to the basecase script

- configuring the transient simulation (test)
  - /glade/work/djk2120/PPEn11trans/cime/scripts/transient/basecases/PPEn11_transient_test
- transient simulation will feature four stages:
  - 1850-1901, reduced output (cycle 1901-1920 forcing)
  - 1901-1984, reduced output
  - 1985-2004, medium output
  - 2005-2014, full output
- cloned hist is already set up to run part0
  - but we'll need to substitute finidat
- creating three scripts to setup the other three parts

### May 5, 2022
- running the second stage of transient (1901-1985)
  - set up via part1.sh
- checking spinup went smoothly
  - would prefer annual output
- transient spinup output files are also unwieldy
  - will switch to new files every five years for monthly and daily

### Sept 26, 2022
- rerunning the ensemble to fix a few bugs
  - qbot issue from GSWP3
  - adding krmax
  - better archiving of lhc key
- updating datm namelist definition
  - /glade/work/oleson/PPE.n11_ctsm5.1.dev030_djk2120/cime/src/components/data_comps_mct/datm/cime_config/namelist_definition_datm.xml
- reclone transient case


### Sept 27, 2022
- needed to rework mods and tether a bit
- submitted one member, and patched things up further
- submitting another twenty:
  - qcmd -- bash run_ens.sh trx/configs/tlai_02.config &> tlai_02.log &