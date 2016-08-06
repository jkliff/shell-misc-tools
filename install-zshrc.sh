#!/usr/bin/env bash

TARGET_GIT_CHECKOUT=~/.zsh-contrib

[[ -d $TARGET_GIT_CHECKOUT ]] || mkdir $TARGET_GIT_CHECKOUT

echo Using $TARGET_GIT_CHECKOUT as git checkout dir
cp -v zsh/zshrc ~/.zshrc

cd $TARGET_GIT_CHECKOUT

if [[ -d zsh-syntax-highlighting ]] ; then
    cd zsh-syntax-highlighting ;
    git pull ;
    cd - ;
else
    git clone git://github.com/zsh-users/zsh-syntax-highlighting.git
fi
pwd
if [[ -d oh-my-zsh ]] ; then
    cd oh-my-zsh ;
    git pull ;
    cd - ;
else
    git clone git://github.com/robbyrussell/oh-my-zsh.git
fi

# create local configuration
touch ~/.zshrc.local

echo "installed. to complete run:"
echo "$ source ~/.zshrc"
