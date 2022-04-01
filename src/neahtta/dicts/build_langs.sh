#!/bin/bash


# A POSIX variable
OPTIND=1         # Reset in case getopts has been used previously in the shell.

# Initialize our own variables:
output_file=""
langpath=""
verbose=0

red=$'\033[31;1m'
green=$'\033[32;1m'
yellow=$'\033[33;1m'
colorend=$'\033[0m'

while getopts "vh?l:s:" opt; do
    case "$opt" in
    h|\?)
        echo ""
        exit 0
        ;;
    v)  verbose=1
        ;;
    l)  langs=$(echo $OPTARG | tr "," " ")
        ;;
    s)  startuplangs=$(echo $OPTARG | tr "," " ")
        ;;
    esac
done

shift $((OPTIND-1))

[ "$1" = "--" ] && shift

langs_flags=$@
script_base="`pwd`"
log_path="`pwd`/error_langs.log"
# echo $log_path

# end argument handling

# todo: startup-langs

# echo "langs=$langs, Leftovers: $langs_flags"
function error {
    msg="$1"
    printf "%s%s%s\n" "$red" "$msg" "$colorend"
}

function log_error {
    error "❗️ couldn't $1 (see build.$1.log)"
    echo $1 >> $log_path
    lang_log="$script_base/build.$1.log"

    if [ $verbose -eq 1 ] ; then
        cat $lang_log
    fi ;
}

function compile_lang {
    lang_log="$script_base/build.$1.log"
    if ! test -e "$GTLANGS/lang-$1/src/Makefile" ; then
        info "autogen"
        cd $GTLANGS/lang-$1 ; ./autogen.sh &>$lang_log && success "autogen" || log_error $1
        info "configure"
        $GTLANGS/lang-$1 ; ./configure $langs_flags &>$lang_log && success "configure" || log_error $1
    fi ;
    info "Building $1"
    cd $GTLANGS/lang-$1 ; make &>$lang_log && success "built $1" || log_error $1
}


function success {
    msg="🌲 $1"
    printf "%s%s%s\n" "$green" "$msg" "$colorend"
}

function info {
    msg="✨ $1"
    printf "%s%s%s\n" "$yellow" "$msg" "$colorend"
}

function compile_startup_lang {
    lang_log="$script_base/build.$1.log"
    if ! test -e "$GTLANGS/lang-$1/src/Makefile" ; then
        info "autogen"
        cd $GTLANGS/lang-$1 ; ./autogen.sh &>$lang_log && success "autogen" || log_error $1
        info "configure"
        cd $GTLANGS/lang-$1 ; ./configure $langs_flags &>$lang_log && success "configure" || log_error $1
    fi ;
    info "Building $1"
    cd $GTLANGS/lang-$1 ; make &>$lang_log && success "built $1" || log_error $1
}

rm $log_path
touch $log_path

for ll in $langs ; do
    compile_lang $ll
done 

for ll in $startuplangs ; do
    compile_startup_lang $ll
done 

errors=`wc -l $log_path | awk {'print $1'}`

if [ "$errors" -gt "0" ] ; then
    error_str="errors compiling: `cat $log_path | tr '\n' ' '`"
    echo "--"
    printf "%s%s%s\n" "$red" "$error_str" "$colorend"
    exit 1
fi

