#!/bin/bash
envtypes=('W1905' 'W2095' 'C285' 'C867' 'ndepp5')
runtype='SASU'
for envtype in ${envtypes[@]}; do
    file="envfiles/"$envtype"_"$runtype".env"
    echo "#!/bin/bash" > $file
    echo "envtype='"$envtype"'" >> $file
    echo "runtype='"$runtype"'" >> $file
    cat template.env >> $file
done
