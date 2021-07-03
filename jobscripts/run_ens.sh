if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./runens.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1


#loop through paramlist
while read p; do
  #create the new case 
  repcase=$casePrefix"_"$p
  echo "--------------------------------------------"
  echo "   creating "$repcase
  echo "--------------------------------------------" 
  cd $SCRIPTS_DIR
  ./create_clone --case $caseDir$casePrefix"/"$repcase --clone $basecase
  cd $caseDir$casePrefix"/"$repcase

  #setup and point to executable
  ./case.setup
  if [ "$exerootFlag" = true ]
  then
      ./xmlchange BUILD_COMPLETE=TRUE
      ./xmlchange EXEROOT=$exeroot
  else
      echo "--------------------------------------------"
      echo "   building "$repcase
      echo "--------------------------------------------" 
      ./case.build
  fi

  # copy user_nl_clm and specify paramfile
  cd $SCRIPTS_DIR$caseDir$casePrefix"/"$repcase
  cp $nlbase user_nl_clm
  pfile=$PARAMS_DIR$p".nc"
  pfilestr="paramfile = '"$pfile"'"
  echo -e "\n"$pfilestr >> user_nl_clm

  # specify finidat if needed
  if [ "$finidatFlag" = true ]
  then
      rfile=$RESTARTS$prevCase"_"$p*".nc"
      rfile=$(echo $rfile) #force wildcard expansion
      rfilestr="finidat ='"$rfile"'"
      echo $rfilestr >> user_nl_clm
  fi
  
  # cat nlmods if needed
  if [ "$nlmodsFlag" = true ]
  then
      nlmods=$NLMODS_DIR$p".txt"
      cat $nlmods >> user_nl_clm
  fi
  
  echo "--------------------------------------------"
  echo "   submitting "$repcase
  echo "--------------------------------------------" 
  ./case.submit


  
done <$paramList
