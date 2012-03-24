#!/bin/bash

cp vimrc/vimrc ~/.vimrc

if [[ ! -d ~/.vim ]] ; then
    mkdir ~/.vim ;
fi

cp -R vimrc/vim/* ~/.vim/
