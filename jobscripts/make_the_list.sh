cd /glade/scratch/djk2120/PPEn11/paramfiles


for x in *.nc
do
    y="$(basename -- $x)"
    echo ${y%.*} >> /glade/u/home/djk2120/clm5ppe/jobscripts/PPEn11/chunk02.txt
done

