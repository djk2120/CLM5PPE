#concatenates all of the postprocessed files

module load nco
source ~/.bashrc
conda activate ppe-py

i=0
files=""
while read p; do

    x=0
    k1=$(echo $p | cut -d, -f2)
    k2=$(echo $p | cut -d, -f3)

    f1="/glade/scratch/djk2120/postp/oaat/"$k1".postp.nc"
    f2="/glade/scratch/djk2120/postp/oaat/"$k2".postp.nc"

    if [ -f $f1 ]; then
	if [ -f $f2 ]; then
	    ((i++))

	    fout="/glade/scratch/djk2120/postp/oaat/pair"$i".nc"
	    files=$files" "$fout
	    ncecat -u minmax $f1 $f2 $fout

	fi
    fi

done</glade/campaign/cgd/tss/projects/PPE/PPEn11_OAAT/helpers/surviving.csv

fout="/glade/scratch/djk2120/postp/oaat/OAAT_surv.nc"
ncecat -u param $files $fout
python label.py
