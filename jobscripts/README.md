# Ensemble generating script

The main script is runens.sh, which ideally would not need to be
    customized to create an ensemble.

Instead customization is achieved through two external files that
    will specify many user-specific environment variables and specify
    the various parameter sets to test.

The ensemble is generated with the following command:
> ./runens.sh this_ensemble.env

The environment file can have any name. Often we might like
    to first spin-up and then run the ensemble. In this case, you
    can create two environment files: e.g. spin_ens.env and run_ens.env

