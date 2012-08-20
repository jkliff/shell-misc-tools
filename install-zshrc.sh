#!/bin/bash
cp zsh/zshrc ~/.zshrc
cd ~/Desktop/dev-tools
if [[ -d zsh-syntax-highlighting ]] ; then
    cd zsh-syntax-highlighting ;
    git pull ;
else
    git clone git://github.com/zsh-users/zsh-syntax-highlighting.git
fi
echo "installed. to complete run:"
echo "$ source ~/.zshrc"
