#!/usr/bin/env bash

set -e
LOGGER=~/install-vim.log

BUNDLES="
    git://github.com/airblade/vim-gitgutter.git         \
    git://github.com/bling/vim-airline.git              \
    git://github.com/derekwyatt/vim-scala.git           \
    git://github.com/digitaltoad/vim-jade.git           \
    git://github.com/flazz/vim-colorschemes.git         \
    git://github.com/groenewege/vim-less.git            \
    git://github.com/guns/vim-sexp.git                  \
    git://github.com/honza/dockerfile.vim.git           \
    git://github.com/kchmck/vim-coffee-script.git       \
    git://github.com/kien/ctrlp.vim.git                 \
    git://github.com/majutsushi/tagbar.git              \
    git://github.com/mustache/vim-mustache-handlebars.git\
    git://github.com/plasticboy/vim-markdown.git        \
    git://github.com/rodjek/vim-puppet.git              \
    git://github.com/scrooloose/nerdtree.git            \
    git://github.com/tfnico/vim-gradle.git              \
    git://github.com/tpope/vim-commentary.git           \
    git://github.com/tpope/vim-dispatch.git             \
    git://github.com/tpope/vim-fireplace.git            \
    git://github.com/tpope/vim-fugitive.git             \
    git://github.com/tpope/vim-leiningen.git            \
    git://github.com/tpope/vim-projectionist.git        \
    git://github.com/tpope/vim-surround.git             \
    git://github.com/venantius/vim-eastwood.git         \
    https://github.com/vim-syntastic/syntastic.git"


function usage {
    echo "Installer for vimrc and bundles"
    echo "Overwrite \$BUNDLE_DIR to set director to other than ~/.vim/bundle"
    echo "Options:"
    echo "    --debug"
    echo "    --backup"
}

function update_project_if_needed {
    if [[ ! -d $1 ]] ; then
        echo -n "fetching... "
        git clone $i >> $LOGGER
        echo ok.
    else
        cd $1
        git remote update >> $LOGGER
        [[ $(git rev-list HEAD...origin/master --count) != 0 ]] && update_project >> $LOGGER
        echo ok.
        cd ..
    fi
}

function update_project {
    echo -n "updating... $1 "
    git pull >> $LOGGER
}

function fix_gotham256_airline {

    # little hack to make sure airline works with gotham256 theme
    AIRLINE=~/.vim/bundle/vim-airline
    COLORSCHEMES=~/.vim/bundle/colorschemes

    [[ ! -e $AIRLINE/autoload/airline/themes/gotham256.vim ]] && \
        ln -vs $COLORSCHEMES/colors/gotham256.vim $AIRLINE/autoload/airline/themes/gotham256.vim >> $LOGGER
    [[ ! -e $AIRLINE/autoload/airline/themes/gotham.vim ]] && \
        ln -vs $COLORSCHEMES/colors/gotham.vim $AIRLINE/autoload/airline/themes/gotham.vim >> $LOGGER
}

check_which () {
    /usr/bin/which "$1" > /dev/null
    [[ $? != "0" ]] && \
        echo "$1 not found. Install for your platform for full features."
}


[[ "$@" == "--debug" ]] && set -x
[[ "$@" == "--help" ]] && usage && exit

[[ -z ${BUNDLE_DIR+x} ]] && BUNDLE_DIR=~/.vim/bundle
echo Using bundle dir [$BUNDLE_DIR]

echo Updating vimrc
cp -v vimrc/vimrc ~/.vimrc >> $LOGGER
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

$CURL ~/.vim/autoload/pathogen.vim https://raw.githubusercontent.com/tpope/vim-pathogen/master/autoload/pathogen.vim

pushd .
cd $BUNDLE_DIR

#for i in $BUNDLES ; do
#    B=$(echo $i | sed -e 's/^.*\/\(.*\).git$/\1/')
echo Updating bundles...
for i in $BUNDLES ; do
    B=$(echo $i | sed -e 's/^.*\/\(.*\).git$/\1/')
    echo -n "... $B "
    update_project_if_needed $B #>> $LOGGER
done

fix_gotham256_airline

popd

echo 'Installing/updating vimrc plugins (not bundles)'
if [[ "$@" == "--backup" ]] ; then
    echo "Backing old plugins up"
    mv -v ~/.vim/plugin ~/.vim/plugin.old-`date +%F-%H%M%S` >> $LOGGER
fi
cp -Rvu vimrc/vim/* ~/.vim/ >> $LOGGER

check_which ctags

