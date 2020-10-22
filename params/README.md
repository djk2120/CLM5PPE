# Automated generation of parameter input files

The main script is `scripts/generate_params_OOP.ipynb` which reads parameter information from a google spreadsheet, organizes ensemble member information, and writes two files to disk for each ensemble member: parameter netcdf file (located in `paramfiles/`) and namelist mods text file (located in `namelist_mods/`).

Functionality is only for one-at-a-time ensemble type. Code will be added to generate a perturbed parameter ensemble with Latin Hypercube sampling for perturbing parameters simultaneously.
