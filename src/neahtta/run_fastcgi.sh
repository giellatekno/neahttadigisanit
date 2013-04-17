#!/bin/sh

PROJDIR="/home/neahtta/kursadict"
ENVDIR="/home/neahtta/neahtta_env"
PIDFILE="$PROJDIR/pidfile.pid"

# PROJDIR="/home/neahtta/kursadict/"
# ENVDIR="/home/neahtta/neahtta_env/"
# PIDFILE="/home/neahtta/kursadict/pidfile.pid"

. $ENVDIR/bin/activate

cd $PROJDIR
if [ -f $PIDFILE ]; then
    kill `cat -- $PIDFILE`
    rm -f -- $PIDFILE
fi

python manage.py runfcgi --pidfile=pidfile.pid --host=127.0.0.1 --port=2323 --method=fork --daemonize

