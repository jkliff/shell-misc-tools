#!env bash

cp -v vimrc/vimrc ~/.vimrc

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

$CURL ~/.vim/autoload/pathogen.vim https://raw.github.com/tpope/vim-pathogen/master/autoload/pathogen.vim

pushd .
cd ~/.vim/bundle

BUNDLES="https://github.com/scrooloose/syntastic.git \
    https://github.com/nvie/vim-flake8.git \
    https://github.com/mattn/emmet-vim.git \
    https://github.com/kien/ctrlp.vim.git \
    https://github.com/scrooloose/nerdtree.git \
    https://github.com/majutsushi/tagbar \
    https://github.com/airblade/vim-gitgutter.git\
    https://github.com/tfnico/vim-gradle\
    https://github.com/groenewege/vim-less"

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

popd

echo 'Installing vimrc plugins (not bundles)'
mv -v ~/.vim/plugin ~/.vim/plugin.old-`date +%F-%H%M%S`
cp -Rv vimrc/vim/* ~/.vim/

/usr/bin/which ctags > /dev/null
[[ $? != "0" ]] && echo "ctags not found. Install for your platform for full features."
