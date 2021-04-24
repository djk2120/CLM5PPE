cd /glade/scratch/djk2120/PPEn08/paramfiles


for x in *.nc
do
    y="$(basename -- $x)"
    echo ${y%.*} >> /glade/u/home/djk2120/clm5ppe/jobscripts/PPEn08/chunk01.txt
done

