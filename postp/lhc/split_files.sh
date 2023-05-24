d='/glade/campaign/asp/djk2120/PPEn11/transient/hist/'

i=0
j=1
printf -v k "%03d" $j
:>"f"$k".txt"
for f in $d*".h0."*; do
    ((i++))
    if (( i==248 )); then
	i=1
	((j++))
	printf -v k "%03d" $j
	:>"f"$k".txt"
    fi
    echo $f >> "f"$k".txt"
done
