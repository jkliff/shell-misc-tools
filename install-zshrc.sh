#!/bin/bash
cp zsh/zshrc ~/.zshrc
cd ~/Desktop/dev-tools
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
