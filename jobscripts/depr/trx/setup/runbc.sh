
s='/glade/work/djk2120/PPEn11trans/cime/scripts/'
casedir=$s"transient/basecases/"
cases=('PPEn11_transient_AD' \
'PPEn11_transient_SASU' \
'PPEn11_transient_postSASU' \
'PPEn11_transient')

#prepare joblist,modlist for tethering
joblist="/glade/u/home/djk2120/clm5ppe/jobscripts/trx/tethered.txt"
modlist="/glade/u/home/djk2120/clm5ppe/jobscripts/trx/modlist.txt"
casemods="/glade/u/home/djk2120/clm5ppe/jobscripts/finidat.sh"
:>$joblist
:>$modlist
i=0
for c in ${cases[@]}; do
    ((i+=1))
    if [ $i -gt 1 ]; then
	echo $casedir$c >> $joblist
	echo $casemods >> $modlist
    fi
done



#submit AD, with the other three segments tethered
template="/glade/u/home/djk2120/clm5ppe/jobscripts/cheyenne.template"
scratch="/glade/scratch/djk2120/"
prevcase="none"
thiscase=$casedir${cases[0]}
cp $joblist $thiscase
cp $modlist $thiscase

bash ../tether.sh $prevcase $scratch $thiscase $casemods $joblist $modlist $template


