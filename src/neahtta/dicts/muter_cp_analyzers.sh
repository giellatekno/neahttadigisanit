# langs: mrj, mhr, fin, rus?
# TODO: just make a Makefile to handle all this

sudo mkdir -p /opt/smi/mhr/bin/
sudo cp $GTHOME/langs/mhr/src/analyser-gt-desc.xfst  /opt/smi/mhr/bin/mhr.fst
sudo cp $GTHOME/langs/mhr/src/generator-gt-norm.xfst /opt/smi/mhr/bin/imhr.fst

sudo mkdir -p /opt/smi/mrj/bin/
sudo cp $GTHOME/langs/mrj/src/analyser-gt-desc.xfst  /opt/smi/mrj/bin/mrj.fst
sudo cp $GTHOME/langs/mrj/src/generator-gt-norm.xfst /opt/smi/mrj/bin/imrj.fst

# sudo mkdir -p /opt/smi/rus/bin/
# sudo cp $GTHOME/langs/rus/src/analyser-gt-desc.xfst  /opt/smi/rus/bin/rus.fst
# sudo cp $GTHOME/langs/rus/src/generator-gt-norm.xfst /opt/smi/rus/bin/irus.fst

sudo mkdir -p /opt/smi/fin/bin/
sudo cp $GTHOME/langs/fin/src/analyser-gt-desc.xfst  /opt/smi/fin/bin/fin.fst
sudo cp $GTHOME/langs/fin/src/generator-gt-norm.xfst /opt/smi/fin/bin/ifin.fst


