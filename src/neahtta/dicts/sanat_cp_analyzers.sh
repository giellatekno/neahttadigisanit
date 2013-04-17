# langs: liv, olo, fkv
# TODO: just make a Makefile to handle all this

svn up $GTHOME/langs/

sudo mkdir -p /opt/smi/olo/bin/
sudo cp $GTHOME/langs/olo/src/analyser-gt-desc.xfst  /opt/smi/olo/bin/olo.fst
sudo cp $GTHOME/langs/olo/src/generator-gt-norm.xfst /opt/smi/olo/bin/iolo.fst

sudo mkdir -p /opt/smi/liv/bin/
sudo cp $GTHOME/langs/liv/src/analyser-gt-desc.xfst  /opt/smi/liv/bin/liv.fst
sudo cp $GTHOME/langs/liv/src/generator-gt-norm.xfst /opt/smi/liv/bin/iliv.fst

sudo mkdir -p /opt/smi/izh/bin/
sudo cp $GTHOME/langs/izh/src/analyser-gt-desc.xfst  /opt/smi/izh/bin/izh.fst
sudo cp $GTHOME/langs/izh/src/generator-gt-norm.xfst /opt/smi/izh/bin/iizh.fst

sudo mkdir -p /opt/smi/fkv/bin/
sudo cp $GTHOME/langs/fkv/src/analyser-gt-desc.xfst  /opt/smi/fkv/bin/fkv.fst
sudo cp $GTHOME/langs/fkv/src/generator-gt-norm.xfst /opt/smi/fkv/bin/ifkv.fst

sudo mkdir -p /opt/smi/fin/bin/
sudo cp $GTHOME/langs/fin/src/analyser-gt-desc.xfst  /opt/smi/fin/bin/fin.fst
sudo cp $GTHOME/langs/fin/src/generator-gt-norm.xfst /opt/smi/fin/bin/ifin.fst

