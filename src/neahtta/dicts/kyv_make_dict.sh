# Script complains if directory has lexc files in it, so copy
echo "Compiling kpv / Komi"

echo "Compiling kpv-engfinrus.xml"
java -Xmx2048m -cp ~/lib/saxon9.jar -Dfile.encoding=UTF8 net.sf.saxon.Transform -it:main $GTHOME/words/dicts/scripts/collect-dict-parts.xsl inDir=$GTHOME/words/dicts/kom2X/src/ > kpv-engfinrus.all.xml
