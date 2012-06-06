#!/bin/bash

if [[ ! -d ~/.vim ]] ; then
    echo 'Creating ~/.vim dir'
    mkdir ~/.vim ;
fi

echo 'Installing dependencies'

# install dependencies.
mkdir -p ~/.vim/autoload ~/.vim/bundle;

CURL=`which curl`
if [[ $CURL != "" ]] ; then
    CURL="$CURL -so"
else
    CURL=`which wget`
    CURL="$CURL -O"
fi

$CURL ~/.vim/autoload/pathogen.vim https://raw.github.com/tpope/vim-pathogen/master/autoload/pathogen.vim

pushd .
cd ~/.vim/bundle
if [[ ! -d syntastic ]] ; then
    git clone https://github.com/scrooloose/syntastic.git
else
    pwd
    cd syntastic
    git pull
fi
popd

echo 'Installing vimrc'

cp vimrc/vimrc ~/.vimrc
cp -R vimrc/vim/* ~/.vim/

/usr/bin/which ctags > /dev/null
[[ $? != "0" ]] && echo "ctags not found. Install for your platform for full features."
