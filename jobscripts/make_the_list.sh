cd /glade/u/home/djk2120/CLM5PPE/params/paramfiles
for x in *.nc
do
    y="$(basename -- $x)"
    echo ${y%.*} >> /glade/u/home/djk2120/CLM5PPE/jobscripts/spinAD.txt
done
