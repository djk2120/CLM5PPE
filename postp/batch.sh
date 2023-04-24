while read exp; do
    if [ $exp != 'CTL2010' ]; then
	sed 's/CTL2010/'$exp'/g' crunch/CTL2010.sh > 'crunch/'$exp'.sh'
    fi
done <exps.txt
