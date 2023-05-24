# for i in {0000..0500}; do
#     echo "LHC"$i
# done

d='/glade/scratch/djk2120/postp/'
k="LHC0000"


module load nco

files=$d"*"$k"*.nc"
ncrcat $files LHC0000.nc
