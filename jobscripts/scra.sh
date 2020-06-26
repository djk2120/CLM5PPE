
"$(read_n $ninst)"


ninst=5
nx=$(wc -l < spinAD.txt)

i=0

while [ $i -lt $nx ]
do
    nl=$((nx-i))
    if [ $nl -lt $ninst ]
    then
	ninst=$nl
    fi

    i=$((i+ninst))
    j=$((j+1))


    echo $j
    lines="$(read_n $ninst)"
    for line in $lines
    do
	echo $line
    done


done < spinAD.txt

