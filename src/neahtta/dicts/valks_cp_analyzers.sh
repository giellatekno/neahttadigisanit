# langs: myv, rus, fin
# TODO: just make a Makefile to handle all this

svn up $GTHOME/langs/

sudo mkdir -p /opt/smi/myv/bin/
sudo cp $GTHOME/langs/myv/src/analyser-gt-desc.xfst  /opt/smi/myv/bin/myv.fst
sudo cp $GTHOME/langs/myv/src/generator-gt-norm.xfst /opt/smi/myv/bin/imyv.fst

sudo mkdir -p /opt/smi/mdf/bin/
sudo cp $GTHOME/langs/mdf/src/analyser-gt-desc.xfst  /opt/smi/mdf/bin/mdf.fst
sudo cp $GTHOME/langs/mdf/src/generator-gt-norm.xfst /opt/smi/mdf/bin/imdf.fst

# sudo mkdir -p /opt/smi/rus/bin/
# sudo cp $GTHOME/langs/rus/src/analyser-gt-desc.xfst  /opt/smi/rus/bin/rus.fst
# sudo cp $GTHOME/langs/rus/src/generator-gt-norm.xfst /opt/smi/rus/bin/irus.fst

sudo mkdir -p /opt/smi/fin/bin/
sudo cp $GTHOME/langs/fin/src/analyser-gt-desc.xfst  /opt/smi/fin/bin/fin.fst
sudo cp $GTHOME/langs/fin/src/generator-gt-norm.xfst /opt/smi/fin/bin/ifin.fst

