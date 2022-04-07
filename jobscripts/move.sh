#!/bin/bash
f=$1
d1=$2
d2=$3
mvkey=$4

mv=0
if [ -f $d2$f ]; then
    echo $d2$f >> collisions.txt
    if [ $mvkey -eq 1 ]; then
	echo "FILE NOT MOVED: "$f" already exists in "$d2
    elif [ $mvkey -eq 2 ]; then
	echo "FILE OVERWRITTEN: "$d2$f
	mv=1
    fi
elif [ $mvkey -gt 0 ]; then
    mv=1
fi


if [ $mv -eq 1 ]; then
    mv $2$1 $3$1
fi

