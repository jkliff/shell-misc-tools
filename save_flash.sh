#!/bin/bash


usage () {
    echo 'burro'
}

echo $?
echo $#

if [[ $# -lt 1 ]] ; then
    usage
    exit -1
fi

DEST=$1
echo "Copying files to $DEST"

if [[ ! -d $DEST ]] ; then
    echo "not a dir"
    #read -p "directory $DEST does not exist. create?"
    exit -2
fi

TMP_PATH=/private/var/folders/cv/r8x66fwd5058d396fbglslyr0000gn/T/

pushd $TMP_PATH

FILES=$(find . -type f -iname 'Flash*' | xargs -n 1 file | sed -e 's/:/ /' | awk '{print $1}')
#FILES=$(find . -type f -iname 'Flash*' | xargs -n 1 file | sed -e 's/:/ /' )


#echo $FILES | xargs -I'{}' echo ln $TMP_PATH'{}' $DEST  #| sed -e  
for f in $FILES ; do
    echo ln "$TMP_PATH$f" $DEST/$f.flv ; 
done
#egrep -i -e "(mpe?g|video)" | 

popd

