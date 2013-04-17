# Script complains if directory has lexc files in it, so copy
echo "Compiling olo-fin.all.xml"
mkdir olo
cp $GTHOME/langs/olo/src/morphology/stems/*.xml `pwd`/olo/
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform \
    -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl \
    inDir=`pwd`/olo/ > olo-fin.all.xml
rm -rf olo

echo "Compiling liv-fin.all.xml"
mkdir liv
cp $GTHOME/langs/liv/src/morphology/stems/*.xml `pwd`/liv/
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform \
    -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl \
    inDir=`pwd`/liv/ > liv-fin.all.xml
rm -rf liv

echo "Compiling fkv-nob.all.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform \
    -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl \
    inDir=$GTHOME/words/dicts/fkvnob/src/ > fkv-nob.all.xml

echo "Compiling izh-fin.all.xml"
mkdir izh
cp $GTHOME/langs/izh/src/morphology/stems/*.xml `pwd`/izh/
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform \
    -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl \
    inDir=`pwd`/izh/ > izh-fin.all.xml
rm -rf izh


echo "Done"
