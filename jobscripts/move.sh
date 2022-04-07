#!/bin/bash
# simple script to move files, with logic to specify whether to overwrite or not
f=$1
d1=$2
d2=$3
mvkey=$4

#mvkey==0, don't move files
#mvkey==1, mv only if you won't overwrite
#mvkey==2, mv with overwrite

mv=0
if [ -f $d2$f ]; then
    echo $d2$f >> collisions.txt  #keep track of filename collisions
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

