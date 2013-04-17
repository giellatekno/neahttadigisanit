# Script complains if directory has lexc files in it, so copy
echo "Compiling yrk / Nenets"
mkdir yrk
cp $GTHOME/langs/yrk/src/morphology/stems/*.xml yrk/
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform \
    -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl \
    inDir=`pwd`/yrk/ > yrk-all.xml
rm -rf yrk

echo "Done"
