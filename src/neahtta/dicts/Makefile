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

# TODO: test vars GTHOME, GTCORE, GTSHARE
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
vada: init yrk fin yrk-lexicon
	@echo "*********************************"
	@echo "** Built targets for vada:     **"
	@echo "**    + yrk lexicon            **"
	@echo "**    + yrk analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "**   (yrk = Nenets)            **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make vada-install"
	@echo "... or copy the fsts in fst/ and ifst/ to their right places."

vada-yrk-install: fst/yrk.fst ifst/iyrk.fst
	mkdir -p /opt/smi/yrk/bin/
	cp $^ /opt/smi/yrk/bin/

vada-install: vada-yrk-install



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
valks: init myv mdf fin myv-lexicon mdf-lexicon
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
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make valks-install"
	@echo "... or copy the fsts in fst/ and ifst/ to their right places."


valks-fin-install: fst/fin.fst ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/

valks-myv-install: fst/myv.fst ifst/imyv.fst
	mkdir -p /opt/smi/myv/bin/
	cp $^ /opt/smi/myv/bin/

valks-mdf-install: fst/mdf.fst ifst/imdf.fst
	mkdir -p /opt/smi/mdf/bin/
	cp $^ /opt/smi/mdf/bin/

valks-install: valks-myv-install \
			   valks-mdf-install \
			   valks-fin-install


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

olo-fin.xml: $(GTHOME)/langs/olo/src/morphology/stems/*.xml
	mkdir olo
	cp $^ olo/
	$(SAXON) inDir=$(pwd)/olo/ > $@
	rm -rf olo/

fkv-nob.xml: $(GTHOME)/words/dicts/fkvnob/src/
	$(SAXON) inDir=$^ > $@

# NOTE: some temporary fixes to add usage to everything, and include <lg>
# node
nob-fkv.xml: $(GTHOME)/words/dicts/nobfkv/src/
	$(SAXON) inDir=$^ > $@.tmp
	cat $@.tmp | sed 's/<e>/<e usage="vd">/g' | \
				 sed 's/  <l /  <lg><l /g'    | \
				 sed 's/<\/l>/<\/l><\/lg>/g'  | \
				 xmllint --format - \
		   	 	 > $@
	rm $@.tmp

liv.all.xml: $(GTHOME)/langs/liv/src/morphology/stems/*.xml
	mkdir liv
	cp $^ liv/
	$(SAXON) inDir=$(pwd)/liv/ > $@
	rm -rf liv/

izh-fin.xml: $(GTHOME)/langs/izh/src/morphology/stems/*.xml
	mkdir izh
	cp $^ izh/
	$(SAXON) inDir=$(pwd)/izh/ > $@
	rm -rf izh/

.PHONY: sanat-lexica
sanat-lexica: olo-fin.xml \
			  liv.all.xml \
			  izh-fin.xml \
			  fkv-nob.xml \
			  nob-fkv.xml

sanat: init olo izh liv fin fkv sanat-lexica
	@echo "*********************************"
	@echo "** Built targets for sanat:    **"
	@echo "**    + olo lexicon            **"
	@echo "**    + fkv lexica             **"
	@echo "**    + liv lexicon            **"
	@echo "**    + izh lexicon            **"
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
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make sanat-install"
	@echo "... or copy the fsts in fst/ and ifst/ to their right places."

sanat-olo-install: fst/olo.fst ifst/iolo.fst
	mkdir -p /opt/smi/olo/bin/
	cp $^ /opt/smi/olo/bin/

sanat-liv-install: fst/liv.fst ifst/iliv.fst
	mkdir -p /opt/smi/liv/bin/
	cp $^ /opt/smi/liv/bin/

sanat-izh-install: fst/izh.fst ifst/iizh.fst
	mkdir -p /opt/smi/izh/bin/
	cp $^ /opt/smi/izh/bin/

sanat-fkv-install: fst/fkv.fst ifst/ifkv.fst
	mkdir -p /opt/smi/fkv/bin/
	cp $^ /opt/smi/fkv/bin/

sanat-install: sanat-olo-install \
   			   sanat-liv-install \
   			   sanat-izh-install \
   			   sanat-fkv-install

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
sme-install: n-sme.fst dict-isme-norm.fst some-n-sme.fst
	cp $^ /opt/smi/sme/bin/

##
### #smeanalysers
##


# NB not copying to fst/ or ifst/ because format is different for these.
n-sme.fst:
dict-isme-norm.fst:
some-n-sme.fst:
	@echo "***********************"
	@echo "** Building sme FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/gt/ ; \
	  make TARGET=sme ; \
	  cp sme/bin/n-sme.fst  $(TARGET_DIR)/n-sme.fst ; \
	  cp sme/bin/some-n-sme.fst  $(TARGET_DIR)/some-n-sme.fst ; \
	  cp sme/bin/dict-isme-norm.fst $(TARGET_DIR)/dict-isme-norm.fst


fst/nob.fst:
	@echo "***********************"
	@echo "** Building nob FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/nob/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/fst/nob.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/ifst/inob.fst

.PHONY: nob
nob: fst/nob.fst

.PHONY: sme
sme: n-sme.fst \
	 dict-isme-norm.fst \
	 some-n-sme.fst

sanit: init sme fin nob sanit-lexica
	@echo "*********************************"
	@echo "** Built targets for sanit:    **"
	@echo "**    + sanit lexica           **"
	@echo "**    + sme analysers          **"
	@echo "**    + fin analysers          **"
	@echo "**    + nob analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make sanit-install"
	@echo "... or copy the fsts in fst/ and ifst/ to their right places."

sanit-fin-install: fst/fin.fst ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/

sanit-nob-install: fst/nob.fst ifst/inob.fst
	mkdir -p /opt/smi/nob/bin/
	cp $^ /opt/smi/nob/bin/

sanit-sme-install: n-sme.fst \
	               dict-isme-norm.fst \
	               some-n-sme.fst
	mkdir -p /opt/smi/sme/bin/
	cp $^ /opt/smi/sme/bin/

sanit-install: sanit-nob-install sanit-sme-install sanit-fin-install


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

.PHONY: sma
sma: dict-sma.fst isma-dict.fst

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

baakoeh: init sma nob baakoeh-lexica
	@echo "*********************************"
	@echo "** Built targets for baakoeh:  **"
	@echo "**    + baakoeh lexica         **"
	@echo "**    + sma analysers          **"
	@echo "**    + nob analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths"
	@echo "    make baakoeh-install"
	@echo "... or copy the fsts in fst/ and ifst/ to their right places."

baakoeh-nob-install: fst/nob.fst ifst/inob.fst
	mkdir -p /opt/smi/nob/bin/
	cp $^ /opt/smi/nob/bin/

baakoeh-sma-install: dict-sma.fst isma-dict.fst
	mkdir -p /opt/smi/sma/bin/
	cp $^ /opt/smi/sma/bin/

baakoeh-install: baakoeh-sma-install \
				 baakoeh-nob-install

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

kyv: init kpv fin kpv-lexica
	@echo "*********************************"
	@echo "** Built targets for kyv:      **"
	@echo "**    + kyv lexicon            **"
	@echo "**    + kpv analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "TODO: install analysers in expected paths"


# This one sets up dirnames, because can't get dirnames from inverse
SOURCES = fst/*.fst

.SUFFIXES: .fst
ISO: $(SOURCES)
	@echo $(foreach fst_file,    \
					$(SOURCES),  \
					$(fst_file)  \
		   )

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
	@echo ""
	@echo ""
	@echo "Is saxon9.lib in the path somewhere?"
	@echo ""
	@echo ""
endif

.PHONY: help
.DEFAULT: help
help:
	@echo "There are several targets for building lexica, FSTs, and installing"
	@echo "FSTs. The main targets to be concerned with are: "
	@echo ""
	@echo " * make sanit"
	@echo " * make baakoeh"
	@echo " * make valks"
	@echo " * make vada"
	@echo " * make kyv"
	@echo ""
	@echo "If running one of these commands complains about missing directories "
	@echo "run the following first:"
	@echo "   make init"
	@echo ""
	@echo "To install FSTs to /opt/smi/ paths and automatically create any missing"
	@echo "directories:"
	@echo ""
	@echo " * make sanit-install"
	@echo " * make baakoeh-install"
	@echo ""
	@echo "NB! Make sure you have saxon9.jar in ~/lib/ !"

.PHONY: install
install: sme-install sma-install install-analysers
	@echo "TODO: "
	@echo "This will copy the analysers that have been built locally here"
	@echo "to respective dirs in /opt/smi/"
	@echo "NB: sme-install, sma-install have separate patterns. also izh might"
	@echo "be matched by"
	@echo " iolo and such, so is it possible to define a length pattern in deps?"

# TODO: here we want to check all of the finalized paths for _installed_ fsts
#       and also compiled dicts/ to make sure that a given install workds

.PHONY: test-sanit
test-sanit: 
	@echo "TODO: "

.PHONY: test-baakoeh
test-baakoeh: 
	@echo "TODO: "

.PHONY: test-kyv
test-kyv: 
	@echo "TODO: "

.PHONY: test-install
test-install: test-sanit \
	 		  test-baakoeh \
	 		  test-kyv
	@echo "TODO: "

.PHONY: all
all: init \
	 vada  \
	 valks \
	 sanat \
	 sanit \
	 baakoeh \
	 kyv
	@echo $(TARGET_DIR)

