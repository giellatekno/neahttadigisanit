# langs: kyv, fin
# TODO: just make a Makefile to handle all this

# svn up $GTHOME/langs/

sudo mkdir -p /opt/smi/kyv/bin/
sudo cp $GTHOME/langs/kyv/src/analyser-gt-desc.xfst  /opt/smi/kyv/bin/kyv.fst
sudo cp $GTHOME/langs/kyv/src/generator-gt-norm.xfst /opt/smi/kyv/bin/ikyv.fst

# sudo mkdir -p /opt/smi/rus/bin/
# sudo cp $GTHOME/langs/rus/src/analyser-gt-desc.xfst  /opt/smi/rus/bin/rus.fst
# sudo cp $GTHOME/langs/rus/src/generator-gt-norm.xfst /opt/smi/rus/bin/irus.fst

sudo mkdir -p /opt/smi/fin/bin/
sudo cp $GTHOME/langs/fin/src/analyser-gt-desc.xfst  /opt/smi/fin/bin/fin.fst
sudo cp $GTHOME/langs/fin/src/generator-gt-norm.xfst /opt/smi/fin/bin/ifin.fst

