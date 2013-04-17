echo "Compiling sme-nob.all.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl inDir=$GTHOME/words/dicts/smenob/src/ > sme-nob.all.xml
echo "Compiling nob-sme.all.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl inDir=$GTHOME/words/dicts/nobsme/src/ > nob-sme.all.xml
echo "Compiling sme-fin.all.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl inDir=$GTHOME/words/dicts/smefin/src/ > sme-fin.all.xml
echo "Compiling fin-sme.all.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl inDir=$GTHOME/words/dicts/finsme/src/ > fin-sme.all.xml
echo "Compiling sma-nob.all.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl inDir=$GTHOME/words/dicts/smanob/src/ > sma-nob.all.xml
echo "Compiling nob-sma.all.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl inDir=$GTHOME/words/dicts/nobsma/src/ > nob-sma.all.xml

echo "Done"
