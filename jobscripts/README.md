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

Likewise the parameter list can have any name. See for example
    mainRun.txt. This is a list of parameter sets for the given
    experiment. Each should correspond to a parameter file upon
    appending .nc

More information forthcoming on how to configure the basecase and
    some ideas for writing scripts to generate the required parameter
    files.