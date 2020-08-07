cd /glade/u/home/djk2120/CLM5PPE/params/scripts/phs_params/paramfiles
for x in *.nc
do
    y="$(basename -- $x)"
    echo ${y%.*} >> /glade/u/home/djk2120/CLM5PPE/jobscripts/PHSens_spinAD.txt
done
cd -
