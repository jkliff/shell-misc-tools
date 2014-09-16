#!env bash

TARGET_GIT_CHECKOUT=${TARGET_GIT_CHECKOUT-~/src}

if [[ ! -d $TARGET_GIT_CHECKOUT ]] ; then
    echo "TARGET_GIT_CHECKOUT is not defined or does not exist. Tried with $TARGET_GIT_CHECKOUT. Aborting."
    exit 1
fi

echo Using $TARGET_GIT_CHECKOUT as git checkout dir

cp -v zsh/zshrc ~/.zshrc
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
