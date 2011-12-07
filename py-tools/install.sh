#!/bin/bash

f="mkpyproject.sh touchpy.sh"

for i in $f ; do
    cp -vi $i $HOME/bin/ ;
    chmod -v +x $HOME/bin/$i ;
done


