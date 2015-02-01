#!env bash

set -e
[[ "$@" == "--debug" ]] && set -x

function usage {
    echo "Installer for vimrc and bundles"
    echo "Overwrite \$BUNDLE_DIR to set director to other than ~/.vim/bundle"
    echo "Options:"
    echo "    --debug"
    echo "    --backup"
}


[[ "$@" == "--help" ]] && usage && exit

[[ -z ${BUNDLE_DIR+x} ]] && BUNDLE_DIR=~/.vim/bundle
echo Using bundle dir [$BUNDLE_DIR]

cp -v vimrc/vimrc ~/.vimrc
[[ ! -d ~/.vim ]] && mkdir ~/.vim

echo 'Installing dependencies'

# install dependencies.
mkdir -p ~/.vim/autoload $BUNDLE_DIR;

CURL=`which curl`
if [[ $CURL != "" ]] ; then
    CURL="$CURL -so"
else
    CURL=`which wget`
    CURL="$CURL -O"
fi

$CURL ~/.vim/autoload/pathogen.vim https://raw.github.com/tpope/vim-pathogen/master/autoload/pathogen.vim

pushd .
cd $BUNDLE_DIR

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
    https://github.com/plasticboy/vim-markdown.git\
    https://github.com/Raimondi/delimitMate.git"

for i in $BUNDLES ; do
    B=$(echo $i | sed -e 's/^.*\/\(.*\).git$/\1/')

    if [[ ! -d $B ]] ; then
        git clone $i
    else
        cd $B
        echo Updating $B
        git pull
        cd -
    fi
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

echo 'Installing/updating vimrc plugins (not bundles)'
[[ "$@" == "--backup" ]] && echo "Backing old plugins up" && mv -v ~/.vim/plugin ~/.vim/plugin.old-`date +%F-%H%M%S`
cp -Rvu vimrc/vim/* ~/.vim/

/usr/bin/which ctags > /dev/null
[[ $? != "0" ]] && echo "ctags not found. Install for your platform for full features."

