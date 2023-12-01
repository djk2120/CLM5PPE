#!/bin/bash
prevcase=$1
thiscase=$2
scratch=$3

#find restart
casename=${thiscase##*/}
p=$(echo $casename | cut -d_ -f4)
prev="PPEn11_transient_"$p
restart=$scratch"restarts/"*$prev*
restart=$(echo $restart)

#comment out existing finidats
cd $thiscase
sed -i 's/^finidat/!&/g' user_nl_clm 

#append new restart
echo -e "\n" >> user_nl_clm
echo 'finidat="'$restart'"'>>user_nl_clm
