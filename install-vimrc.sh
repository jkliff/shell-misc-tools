#!/bin/bash

if [[ ! -d ~/.vim ]] ; then
    echo 'Creating ~/.vim dir'
    mkdir ~/.vim ;
fi

echo 'Installing dependencies'

# install dependencies.
mkdir -p ~/.vim/autoload ~/.vim/bundle;
curl -so ~/.vim/autoload/pathogen.vim https://raw.github.com/tpope/vim-pathogen/master/autoload/pathogen.vim

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

/usr/bin/which -s ctags
[[ $? != "0" ]] && echo "ctags not found. Install for your platform for full features."
