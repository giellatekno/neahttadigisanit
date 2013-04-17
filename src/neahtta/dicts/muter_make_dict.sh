
# Script complains if directory has lexc files in it, so copy
echo "Compiling mrj / Western Mari"
mkdir mrj
cp $GTHOME/langs/mrj/src/morphology/stems/*.xml mrj/
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform \
    -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl \
    inDir=`pwd`/mrj/ > mrj-all.xml
rm -rf mrj

echo "Compiling mhr / Eastern Mari"
mkdir mhr
cp $GTHOME/langs/mhr/src/morphology/stems/*.xml mhr/
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform \
    -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl \
    inDir=`pwd`/mhr/ > mhr-all.xml
rm -rf mhr

echo "Done"
