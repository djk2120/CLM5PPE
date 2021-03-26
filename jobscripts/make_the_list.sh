cd /glade/work/kdagon/CLM5PPE/params/paramfiles

for x in *.nc
do
    y="$(basename -- $x)"
    echo ${y%.*} >> /glade/u/home/djk2120/clm5ppe/ens001/ens001.txt
done
cd -
