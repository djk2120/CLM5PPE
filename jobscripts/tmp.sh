if [ $# -eq 0 ]
then
    echo "ERROR: please specify format file"
    echo "   ex: ./runens.sh spinAD.env"
    exit 1
fi

#set up environment variables
source $1
jobdir=$(pwd)"/"



#loop through paramlist
failedrun=0
already=0
htapes=('h0' 'h1' 'h2' 'h3' 'h4' 'h5' 'h7')

pad=''
histdir=$SCRATCH$codebase"/hist"$pad$runtype"/"$ensname"/"


echo $histdir
