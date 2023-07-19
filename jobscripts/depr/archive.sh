#!/bin/bash

source EmBE/configs/EmBE.config

REST=$CAMPAIGN"PPEn11/EmBE/rest/"
mkdir -p $REST
HIST=$CAMPAIGN"PPEn11/EmBE/hist/"
mkdir -p $HIST
SPIN=$CAMPAIGN"PPEn11/EmBE/spin/"
mkdir -p $SPIN


prod=${stages[-1]}
for stage in ${stages[@]}; do
    if [ $stage = $prod ]; then
	HDIR=$HIST
    else
	HDIR=$SPIN
    fi
    while read p; do
	c=$SCRATCH$stage'_'$p'/run/'
	cp $c*".clm2.r."* $REST     #archive restarts
	cp $c*".clm2.h"*"."* $HDIR  #archive history
    done<$paramList
done










