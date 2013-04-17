export GTHOME=~/gtsvn/
export GTCORE=$GTHOME/gtcore/

mkdir gtsvn
cd gtsvn
svn co https://victorio.uit.no/langtech/trunk/words/ words
svn co https://victorio.uit.no/langtech/trunk/gtcore gtcore
svn co https://victorio.uit.no/langtech/trunk/gt gt
svn co https://victorio.uit.no/langtech/trunk/st st
svn co https://victorio.uit.no/langtech/trunk/langs langs

cd $GTHOME/gt/
make TARGET=sme

cd $GTHOME/st/nob/src
make

cd $GTHOME/langs/sma
./autogen.sh && ./configure && make target=xfst

cd $GTHOME/langs/fin
./autogen.sh && ./configure && make target=xfst


