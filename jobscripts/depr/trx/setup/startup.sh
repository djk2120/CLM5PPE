#check out PPEn11 codebase
cd /glade/work/djk2120
git clone -b branch_tags/PPE.n11_ctsm5.1.dev030 https://github.com/ESCOMP/CTSM.git PPEn11trans
cd PPEn11trans
./manage_externals/checkout_externals


#grab Keith's mods
d1='/glade/work/djk2120/PPEn11trans/src/'
d2='/glade/work/oleson/PPE.n11_ctsm5.1.dev030_djk2120/src/'
ms=("biogeophys" "biogeochem" "main")
for m in ${ms[@]};do 
    cd $d1$m
    for f in *.F90; do
	k=$d2$m"/"$f
	nx=$(diff $f $k | wc -l)
	if [ $nx -gt 0 ]; then
	    echo $f
	    cp $f ${f%.*}".old"
	    cp $k $f
	fi
    done
done

