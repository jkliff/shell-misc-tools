#!/bin/bash

BIN=$HOME/bin
if [[ ! -e $BIN ]] ; then
    mkdir $BIN
fi

INCLUDE="timetracker/tt.py misc/bulk_image_convert.py"

d=$(date +%s)
for x in $INCLUDE ; do
    y=$(basename $x)
    if [[ -e $BIN/$y ]] ; then
        b=$BIN/.$y-$d
        echo "Saving backup of exisgin $x to $b"
        cp $BIN/$y $b
    fi
    cp -v $x $BIN
done

echo $PATH | grep -q $BIN
if [[ $? != "0" ]] ; then
    echo "WARNING: $BIN does not seem to be in your PATH."
fi
