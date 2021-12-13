source $1
tape='r'
fails=$(basename $1 .config)"_"$tape"_fails.txt"

while read p; do

  #create the new case name
  repcase=$casePrefix"_"$p
  cd $SCRIPTS_DIR
  cd $caseDir$repcase
  ./case.submit

done <$fails
