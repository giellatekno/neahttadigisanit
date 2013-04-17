# langs: yrk, fin
# TODO: just make a Makefile to handle all this

# svn up $GTHOME/langs/

sudo mkdir -p /opt/smi/yrk/bin/
sudo cp $GTHOME/langs/yrk/src/analyser-gt-desc.xfst  /opt/smi/yrk/bin/yrk.fst
sudo cp $GTHOME/langs/yrk/src/generator-gt-norm.xfst /opt/smi/yrk/bin/iyrk.fst

# sudo mkdir -p /opt/smi/rus/bin/
# sudo cp $GTHOME/langs/rus/src/analyser-gt-desc.xfst  /opt/smi/rus/bin/rus.fst
# sudo cp $GTHOME/langs/rus/src/generator-gt-norm.xfst /opt/smi/rus/bin/irus.fst

sudo mkdir -p /opt/smi/fin/bin/
sudo cp $GTHOME/langs/fin/src/analyser-gt-desc.xfst  /opt/smi/fin/bin/fin.fst
sudo cp $GTHOME/langs/fin/src/generator-gt-norm.xfst /opt/smi/fin/bin/ifin.fst

