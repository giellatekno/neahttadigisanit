#######################
##                   ##
## Table of Contents ##
##                   ##
#######################

# Some helpful tags for jumping around

###         #Analyzers
###          #finanalysers
###         
###         #vadatargets
###          #yrkanalysers
###          #vadalexicon
###         
###         #valkstargets
###          #myvanalysers
###          #mdfanalysers
###         
###         #sanattargets
###          #oloanalysers
###          #livanalysers
###          #fkvanalysers
###          #izhanalysers
###          #sanatlexica
###         
###         #sanittargets
###          #sanitlexica
###          #smeanalysers
###         
###         #baakoehtargets
###          #smaanalysers
###          #baakoehlexica
###         
###         #kyvtargets
###          #kpvanalysers
###          #kyvlexica
###         
###         #Globaltargets

# TODO: test GTHOME, GTCORE, GTSHARE
# TODO: run a check on svn directories to print out what is updated since the
#       last build of the various targets.

COLLECT_PARTS := $(GTHOME)/words/dicts/scripts/collect-dict-parts.xsl 
SAXON := java -Xmx2048m -cp ~/lib/saxon9.jar \
		 -Dfile.encoding=UTF8 net.sf.saxon.Transform \
		 -it:main $(COLLECT_PARTS)

TARGET_DIR := $(shell pwd)
pwd := $(shell pwd)

define compile-lexicon =
	$(SAXON)
endef


#####
##### #Analyzers used in nearly everything
#####

##
### #finanalysers
##

fst/fin.fst:
	@echo "***********************"
	@echo "** Building fin FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/fin/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/fin.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/ifin.fst

.PHONY: fin
fin: fst/fin.fst



#####
##### #vadatargets
#####

##
### #yrkanalysers
##

fst/yrk.fst:
	@echo "***********************"
	@echo "** Building yrk FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/yrk/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/yrk.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/iyrk.fst

.PHONY: yrk
yrk: fst/yrk.fst

##
### #vadalexicon
##

yrk-all.xml: $(GTHOME)/langs/yrk/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building yrk lexicon **"
	@echo "**************************"
	@echo ""
	mkdir yrk
	cp $^ yrk/
	$(SAXON) inDir=$(pwd)/yrk/ > yrk-all.xml
	rm -rf yrk/

.PHONY: yrk-lexicon
yrk-lexicon: yrk-all.xml

.PHONY: vada
vada: yrk fin yrk-lexicon
	@echo "*********************************"
	@echo "** Built targets for vada:     **"
	@echo "**    + yrk lexicon            **"
	@echo "**    + yrk analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "**   (yrk = Nenets)            **"
	@echo "*********************************"
	@echo "TODO: install analysers in expected paths"





#####
##### #valkstargets
#####

##
### #myvanalysers
##

fst/myv.fst:
	@echo "***********************"
	@echo "** Building myv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/myv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/myv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/imyv.fst

.PHONY: myv
myv: fst/myv.fst


##
### #mdfanalysers
##

fst/mdf.fst:
	@echo "***********************"
	@echo "** Building mdf FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/mdf/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/mdf.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/imdf.fst

.PHONY: mdf
mdf: fst/mdf.fst

myv-all.xml: $(GTHOME)/langs/myv/src/morphology/stems/*.xml
	mkdir myv
	cp $^ myv/
	$(SAXON) inDir=$(pwd)/myv/ > myv-all.xml
	rm -rf myv/

mdf-all.xml: $(GTHOME)/langs/mdf/src/morphology/stems/*.xml
	mkdir mdf
	cp $^ mdf/
	$(SAXON) inDir=$(pwd)/mdf/ > mdf-all.xml
	rm -rf mdf/

.PHONY: myv-lexicon
myv-lexicon: myv-all.xml

.PHONY: mdf-lexicon
mdf-lexicon: mdf-all.xml
	
.PHONY: valks
valks: myv mdf fin myv-lexicon mdf-lexicon
	@echo "*********************************"
	@echo "** Built targets for valks:    **"
	@echo "**    + myv, mdf lexica        **"
	@echo "**    + myv analysers          **"
	@echo "**    + mdf analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "**   (myv = Erzya)             **"
	@echo "**   (mdf = Moksha)            **"
	@echo "*********************************"
	@echo "TODO: install analysers in expected paths"





#####
##### #sanattargets
#####

##
### #oloanalysers
##

fst/olo.fst:
	@echo "***********************"
	@echo "** Building olo FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/olo/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/olo.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/iolo.fst

.PHONY: olo
olo: fst/olo.fst

##
### #livanalysers
##

fst/liv.fst:
	@echo "***********************"
	@echo "** Building liv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/liv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/liv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/iliv.fst

.PHONY: liv
liv: fst/liv.fst

##
### #fkvanalysers
##

fst/fkv.fst:
	@echo "***********************"
	@echo "** Building fkv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/fkv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/fkv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/ifkv.fst

.PHONY: fkv
fkv: fst/fkv.fst

##
### #izhanalysers
##

fst/izh.fst:
	@echo "***********************"
	@echo "** Building izh FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/izh/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/izh.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/iizh.fst

.PHONY: izh
izh: fst/izh.fst

##
### #sanatlexica
##

olo-fin.all.xml: $(GTHOME)/langs/olo/src/morphology/stems/*.xml
	mkdir olo
	cp $^ olo/
	$(SAXON) inDir=$(pwd)/olo/ > $@
	rm -rf olo/


liv-fin.all.xml: $(GTHOME)/langs/liv/src/morphology/stems/*.xml
	mkdir liv
	cp $^ liv/
	$(SAXON) inDir=$(pwd)/liv/ > $@
	rm -rf liv/

izh-fin.all.xml: $(GTHOME)/langs/izh/src/morphology/stems/*.xml
	mkdir izh
	cp $^ izh/
	$(SAXON) inDir=$(pwd)/izh/ > $@
	rm -rf izh/

.PHONY: sanat-lexica
sanat-lexica: olo-fin.all.xml \
			  liv-fin.all.xml \
			  izh-fin.all.xml

# TODO: fkv

sanat: olo izh liv fin fkv sanat-lexica
	@echo "*********************************"
	@echo "** Built targets for valks:    **"
	@echo "**    + olo lexicon            **"
	@echo "**    + olo analysers          **"
	@echo "**    + liv analysers          **"
	@echo "**    + izh analysers          **"
	@echo "**    + fkv analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "**   (olo = Olonets)           **"
	@echo "**   (liv = Livonian)          **"
	@echo "**   (izh = Izhorian)          **"
	@echo "**   (fkv = Kven)              **"
	@echo "*********************************"
	@echo "TODO: install analysers in expected paths"



#####
##### #sanittargets
#####

##
### #sanitlexica
##

# NB: these are different than the langs/ lexica
sme-nob.all.xml: $(GTHOME)/words/dicts/smenob/src/
	$(SAXON) inDir=$^ > $@

sme-fin.all.xml: $(GTHOME)/words/dicts/smefin/src/
	$(SAXON) inDir=$^ > $@

fin-sme.all.xml: $(GTHOME)/words/dicts/finsme/src/
	$(SAXON) inDir=$^ > $@

nob-sme.all.xml: $(GTHOME)/words/dicts/nobsme/src/
	$(SAXON) inDir=$^ > $@

sanit-lexica: fin-sme.all.xml \
			  nob-sme.all.xml \
			  sme-fin.all.xml \
			  sme-nob.all.xml

# NB: sme analyzer build is different, as well as target fst file names
# also there is one additional analyser that comes out of this, which is
# the relaxed analyser.
#
# As these have different names, they won't be matched by pattern in other install
# target, so making a target for them here.
sme-install: n-sme.fst dict-isme-norm.fst some-sme.fst
	cp $^ /opt/smi/sme/bin/

##
### #smeanalysers
##

n-sme.fst:
dict-isme-norm.fst:
some-sme.fst:
	@echo "***********************"
	@echo "** Building sme FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/gt/ ; \
	  make TARGET=sme ; \
	  cp sme/bin/n-sme.fst  $(TARGET_DIR)/n-sme.fst ; \
	  cp sme/bin/some-sme.fst  $(TARGET_DIR)/some-sme.fst ; \
	  cp sme/bin/dict-isme-norm.fst $(TARGET_DIR)/dict-isme-norm.fst

# This is also different from the rest, involves st/ 
nob: 
	cd $(GTHOME)/st/nob/src/ ; \
	  make ; \
	  cp ../bin/nob.fst   $(TARGET_DIR)/fst/nob.fst ; \
	  cp ../bin/inob.fst  $(TARGET_DIR)/ifst/inob.fst

.PHONY: sme
sme: n-sme.fst dict-isme-norm.fst some-sme.fst

sanit: sme fin nob sanit-lexica
	@echo "*********************************"
	@echo "** Built targets for valks:    **"
	@echo "**    + sanit lexica           **"
	@echo "**    + sme analysers          **"
	@echo "**    + fin analysers          **"
	@echo "**    + nob analysers          **"
	@echo "*********************************"
	@echo "TODO: install analysers in expected paths"



#####
##### #baakoehtargets
#####

##
### #smaanalysers
##

dict-sma.fst:
isma-dict.fst:
	@echo "***********************"
	@echo "** Building sma FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/sma/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-dict-gt-desc.xfst  $(TARGET_DIR)/dict-sma.fst ; \
	  cp src/generator-dict-gt-norm.xfst $(TARGET_DIR)/isma-dict.fst

sma-install: dict-sma.fst isma-dict.fst
	cp $^ /opt/smi/sma/bin/

.PHONY: sma
sma: sma.fst isma.fst

##
### #baakoehlexica
##

# NB: these are more similar to sme lexicon, but FST differs.
sma-nob.all.xml: $(GTHOME)/words/dicts/smanob/src/
	$(SAXON) inDir=$^ > $@

nob-sma.all.xml: $(GTHOME)/words/dicts/nobsma/src/
	$(SAXON) inDir=$^ > $@

baakoeh-lexica: sma-nob.all.xml \
				nob-sma.all.xml

baakoeh: sma nob baakoeh-lexica
	@echo "*********************************"
	@echo "** Built targets for baakoeh:  **"
	@echo "**    + baakoeh lexica         **"
	@echo "**    + sma analysers          **"
	@echo "**    + nob analysers          **"
	@echo "*********************************"
	@echo "TODO: install analysers in expected paths"




#####
##### #kyvtargets
#####

##
### #kpvanalysers
##

kpv.fst:
ikpv.fst:
	@echo "***********************"
	@echo "** Building kpv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/kpv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/kpv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/ikpv.fst

.PHONY: kpv
kpv: kpv.fst ikpv.fst

kpv-engfinrus.all.xml: $(GTHOME)/words/dicts/kom2X/src/
	$(SAXON) inDir=$^ > $@

##
### #kyvlexica
##

.PHONY: kpv-lexica
kpv-lexica: kpv-engfinrus.all.xml

kyv: kpv fin kpv-lexica
	@echo "*********************************"
	@echo "** Built targets for baakoeh:  **"
	@echo "**    + kyv lexicon            **"
	@echo "**    + kpv analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "TODO: install analysers in expected paths"


# This one sets up dirnames, because can't get dirnames from inverse
SOURCES = fst/*.fst

.SUFFIXES: .fst .omg
ISO:
%.omg: fst/%.fst
	echo $*

# mkdir -p /opt/smi/$(notdir $(basename $<))/bin/
# cp $< /opt/smi/$(notdir $(basename $<))/bin/$(notdir $<)

iISO:
/opt/smi/%/bin/%.fst: ifst/%.fst
	@echo $<
	@printf "mkdir -p /opt/smi/$(basename $^)/bin"
	@printf "cp $< $^"

install-analysers: ISO iISO

#####
##### #Globaltargets
#####

INITTED := $(wildcard fst)

ifneq ($(strip $(INITTED)),)
init:
	@echo "Already initted..."
else
init:
	mkdir fst
	mkdir ifst
endif

.PHONY: help
.DEFAULT: help
help:
	@echo "OMG"

.PHONY: install
install: sme-install sma-install install-analysers
	@echo "TODO: "
	@echo "This will copy the analysers that have been built locally here"
	@echo "to respective dirs in /opt/smi/"
	@echo "NB: sme-install, sma-install have separate patterns. also izh might"
	@echo "be matched by"
	@echo " iolo and such, so is it possible to define a length pattern in deps?"

# TODO: sanit 
.PHONY: all
all: init \
	 vada  \
	 valks \
	 sanat \
	 baakoeh \
	 kyv
	@echo $(TARGET_DIR)

