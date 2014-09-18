#!env bash

BIN=$HOME/bin
BACKUP=$BIN/.backup

[[ -e $BIN ]] || mkdir $BIN
[[ -e $BACKUP ]] || mkdir $BACKUP

INCLUDE="timetracker/tt.py misc/bulk_image_convert.py template_touch/tpltouch worklog/wl.py"

d=$(date +%s)

for x in $INCLUDE ; do
    y=$(basename $x)
    if [[ -e $BIN/$y ]] ; then
        b=$BACKUP/$y-$d
        echo "Saving backup of existing $x to $b"
        cp -v $BIN/$y $b
    fi
    cp -v $x $BIN
done

echo $PATH | grep -q $BIN
if [[ $? != "0" ]] ; then
    echo "WARNING: $BIN does not seem to be in your PATH."
fi
