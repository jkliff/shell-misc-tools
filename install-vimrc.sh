#!env bash

set -e
LOGGER=~/install-vim.log

echo Updating vimrc
cp -v vimrc/vimrc ~/.vimrc >> $LOGGER

if [[ ! -d ~/.vim ]] ; then
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

$CURL ~/.vim/autoload/pathogen.vim https://raw.github.com/tpope/vim-pathogen/master/autoload/pathogen.vim >> $LOGGER

pushd .
cd ~/.vim/bundle

BUNDLES="https://github.com/scrooloose/syntastic.git \
    https://github.com/nvie/vim-flake8.git \
    https://github.com/mattn/emmet-vim.git \
    https://github.com/kien/ctrlp.vim.git \
    https://github.com/scrooloose/nerdtree.git \
    git://github.com/tpope/vim-fugitive.git \
    https://github.com/majutsushi/tagbar.git \
    https://github.com/airblade/vim-gitgutter.git\
    https://github.com/tfnico/vim-gradle.git \
    https://github.com/groenewege/vim-less.git \
    https://github.com/honza/dockerfile.vim.git \
    https://github.com/derekwyatt/vim-scala.git \
    https://github.com/plasticboy/vim-markdown.git \
    git://github.com/digitaltoad/vim-jade.git"

function update_project {
    if [[ ! -d $1 ]] ; then
        git clone $i
    else
        cd $1
        echo Updating $1
        git pull
        cd -
    fi
}

echo Updating bundles...
for i in $BUNDLES ; do
    B=$(echo $i | sed -e 's/^.*\/\(.*\).git$/\1/')
    echo .. $B
    update_project $B >> $LOGGER
done

#mkdir -v ~/.vim/tmp
#cd ~/.vim/tmp
#git clone https://github.com/flazz/vim-colorschemes.git

cd ~/.vim
if [[ ! -e bundle/colorschemes ]] ; then
    git clone https://github.com/flazz/vim-colorschemes.git bundle/colorschemes
else
    cd bundle/colorschemes ; git pull
fi

popd

echo 'Installing vimrc plugins (not bundles)'
mv -v ~/.vim/plugin ~/.vim/plugin.old-`date +%F-%H%M%S`
cp -Rv vimrc/vim/* ~/.vim/ >> $LOGGER

/usr/bin/which ctags > /dev/null
[[ $? != "0" ]] && echo "ctags not found. Install for your platform for full features."

