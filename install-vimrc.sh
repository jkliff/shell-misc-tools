#!/bin/bash

cp vimrc/vimrc ~/.vimrc

if [[ ! -d ~/.vim ]] ; then
    mkdir ~/.vim ;
fi

cp -R vimrc/vim/* ~/.vim/

/usr/bin/which -s ctags
[[ $? != "0" ]] && echo "ctags not found. Install for your platform for full features."
