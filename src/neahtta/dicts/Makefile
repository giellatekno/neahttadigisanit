#######################
##                   ##
## Table of Contents ##
##                   ##
#######################

# Some helpful tags for jumping around

###         #Analyzers
###          #finanalysers
###          #rusanalysers TODO
###         
###         #guusaawtargets
###          #hdnanalysers
###          #guusaawlexicon
###         
###         #pikiskwewinatargets
###          #crkanalysers
###          #pikiskwewinalexicon
###         
###         #saantargets
###          #smsanalysers
###          #saanlexicon
###         
###         #vadatargets
###          #yrkanalysers
###          #vadalexicon
###         
###         #valkstargets
###          #myvanalysers
###          #mdfanalysers
###         
###         #mutertargets
###          #mhranalysers
###          #mrjanalysers
###          #muterlexicon
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
###         #ereytargets
###          #somanalysers
###          #somlexica
###         
###         #guusaawtargets
###          #hdnanalysers
###          #hdnlexica
###         
###         #Globaltargets

# TODO: test vars GTHOME, GTCORE, GTSHARE
# TODO: run a check on svn directories to print out what is updated since the
#       last build of the various targets.

COLLECT_PARTS := $(GTHOME)/words/dicts/scripts/collect-dict-parts.xsl 
SAXON := java -Xmx2048m -cp ~/lib/saxon9.jar \
		 -Dfile.encoding=UTF8 net.sf.saxon.Transform \
		 -it:main $(COLLECT_PARTS)

COLLECT_PARTS_SME_NOB := $(GTHOME)/words/dicts/scripts/collect-dict-parts-smenob.xsl
SAXON_SME_NOB := java -Xmx2048m -cp ~/lib/saxon9.jar \
		 -Dfile.encoding=UTF8 net.sf.saxon.Transform \
		 -it:main $(COLLECT_PARTS_SME_NOB)

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

tmp_fst/fin.fst:
	@echo "***********************"
	@echo "** Building fin FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/fin/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/fin.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/ifin.fst

.PHONY: fin
fin: tmp_fst/fin.fst

# TODO: actually in st

##
### #rusanalysers
##

tmp_fst/rus.fst:
	@echo "***********************"
	@echo "** Building rus FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/rus/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/rus.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/irus.fst

.PHONY: rus
rus: tmp_fst/rus.fst



#####
##### #guusaawtargets
#####

##
### #hdnanalysers
##

fst/hdn.fst:
	@echo "***********************"
	@echo "** Building hdn FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/hdn/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/hdn.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/ihdn.fst

.PHONY: hdn
hdn: tmp_fst/hdn.fst

##
### #guusaawlexicon
##

hdn-all.xml: $(GTHOME)/words/dicts/hdneng/src/*.xml
	@echo "**************************"
	@echo "** Building hdn lexicon **"
	@echo "**************************"
	@echo ""
	$(SAXON) inDir=$(GTHOME)/words/dicts/hdneng/src/ > hdn-all.xml

.PHONY: hdn-lexicon
guusaaw-lexica: hdn-all.xml

.PHONY: guusaaw
guusaaw: init hdn eng guusaaw-lexica
	@echo "*************************************"
	@echo "** Built targets for guusaaw:      **"
	@echo "**    + hdn lexicon                **"
	@echo "**    + hdn analysers              **"
	@echo "**    + eng analysers              **"
	@echo "*************************************"
	@echo "**   (hdn = Northern Haida)        **"
	@echo "*************************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make guusaaw-install"
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

guusaaw-hdn-install: tmp_fst/hdn.fst tmp_ifst/ihdn.fst
	mkdir -p /opt/smi/hdn/bin/
	cp $^ /opt/smi/hdn/bin/
	chmod a+x /opt/smi/hdn/bin/*.fst

guusaaw-install: guusaaw-hdn-install




#####
##### #pikiskwewinatargets
#####

##
### #crkanalysers
##

tmp_fst/crk.fst:
	@echo "***********************"
	@echo "** Building crk FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/crk/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/crk.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/icrk.fst

.PHONY: crk
crk: tmp_fst/crk.fst

##
### #pikiskwewinalexicon
##

crk-all.xml: $(GTHOME)/words/dicts/crkeng/src/*.xml
	@echo "**************************"
	@echo "** Building crk lexicon **"
	@echo "**************************"
	@echo ""
	$(SAXON) inDir=$(GTHOME)/words/dicts/crkeng/src/ > crk-all.xml

.PHONY: crk-lexicon
pikiskwewina-lexica: crk-all.xml

.PHONY: pikiskwewina
pikiskwewina: init crk eng pikiskwewina-lexica
	@echo "*************************************"
	@echo "** Built targets for pikiskwewina: **"
	@echo "**    + crk lexicon                **"
	@echo "**    + crk analysers              **"
	@echo "**    + eng analysers              **"
	@echo "*************************************"
	@echo "**   (crk = Plains Cree)           **"
	@echo "*************************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make pikiskwewina-install"
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

pikiskwewina-crk-install: tmp_fst/crk.fst tmp_ifst/icrk.fst
	mkdir -p /opt/smi/crk/bin/
	cp $^ /opt/smi/crk/bin/
	chmod a+x /opt/smi/crk/bin/*.fst

pikiskwewina-install: pikiskwewina-crk-install


#####
##### #saantargets
#####

##
### #smsanalysers
##

tmp_fst/sms.fst:
	@echo "***********************"
	@echo "** Building sms FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/sms/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/sms.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/isms.fst

.PHONY: sms
sms: tmp_fst/sms.fst

##
### #saanlexicon
##

sms-all.xml: $(GTHOME)/langs/sms/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building sms lexicon **"
	@echo "**************************"
	@echo ""
	mkdir sms
	cp $^ sms/
	$(SAXON) inDir=$(pwd)/sms/ > sms-all.xml
	rm -rf sms/

.PHONY: sms-lexicon
saan-lexica: sms-all.xml

.PHONY: saan
saan: init sms fin saan-lexica
	@echo "*********************************"
	@echo "** Built targets for saan:     **"
	@echo "**    + sms lexicon            **"
	@echo "**    + sms analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "**   (sms = Skolt)             **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make saan-install"
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

saan-sms-install: tmp_fst/sms.fst tmp_ifst/isms.fst
	mkdir -p /opt/smi/sms/bin/
	cp $^ /opt/smi/sms/bin/
	chmod a+x /opt/smi/sms/bin/*.fst

saan-install: saan-sms-install


#####
##### #vadatargets
#####

##
### #yrkanalysers
##

tmp_fst/yrk.fst:
	@echo "***********************"
	@echo "** Building yrk FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/yrk/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/yrk.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/iyrk.fst

.PHONY: yrk
yrk: tmp_fst/yrk.fst

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
vada-lexica: yrk-all.xml

.PHONY: vada
vada: init yrk fin vada-lexica
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
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

vada-yrk-install: tmp_fst/yrk.fst tmp_ifst/iyrk.fst
	mkdir -p /opt/smi/yrk/bin/
	cp $^ /opt/smi/yrk/bin/
	chmod a+x /opt/smi/yrk/bin/*.fst

vada-install: vada-yrk-install

#####
##### #mutertargets
#####

##
### #mhranalysers
##

tmp_fst/mhr.fst:
	@echo "***********************"
	@echo "** Building mhr FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/mhr/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/mhr.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/imhr.fst

##
### #mrjanalysers
##

tmp_fst/mrj.fst:
	@echo "***********************"
	@echo "** Building mrj FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/mrj/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/mrj.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/imrj.fst

.PHONY: mhr
mhr: tmp_fst/mhr.fst

.PHONY: mrj
mrj: tmp_fst/mrj.fst

##
### #muterlexicon
##


mrj-all.xml: $(GTHOME)/langs/mrj/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building mrj lexicon **"
	@echo "**************************"
	@echo ""
	mkdir mrj
	cp $^ mrj/
	$(SAXON) inDir=$(pwd)/mrj/ > mrj-all.xml
	rm -rf mrj/

mhr-all.xml: $(GTHOME)/langs/mhr/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building mhr lexicon **"
	@echo "**************************"
	@echo ""
	mkdir mhr
	cp $^ mhr/
	$(SAXON) inDir=$(pwd)/mhr/ > mhr-all.xml
	rm -rf mhr/

.PHONY: muter-lexicon
muter-lexica: mhr-all.xml mrj-all.xml

# TODO: rus
.PHONY: muter
muter: init mrj mhr fin muter-lexicon
	@echo "*********************************"
	@echo "** Built targets for muter:     **"
	@echo "**    + mhr lexicon            **"
	@echo "**    + mrj lexicon            **"
	@echo "**    + mhr analysers          **"
	@echo "**    + mrj analysers          **"
	@echo "**    + rus analysers TODO     **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "**   (mhr = Eastern Mari)      **"
	@echo "**   (mrj = Western Mari)      **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make muter-install"
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

muter-mhr-install: tmp_fst/mhr.fst tmp_ifst/imhr.fst
	mkdir -p /opt/smi/mhr/bin/
	cp $^ /opt/smi/mhr/bin/
	chmod a+x /opt/smi/mhr/bin/*.fst

muter-mrj-install: tmp_fst/mrj.fst tmp_ifst/imrj.fst
	mkdir -p /opt/smi/mrj/bin/
	cp $^ /opt/smi/mrj/bin/
	chmod a+x /opt/smi/mrj/bin/*.fst

# muter-rus-install: tmp_fst/rus.fst tmp_ifst/irus.fst
muter-rus-install:
	@echo "TODO: rus"
	# mkdir -p /opt/smi/rus/bin/
	# cp $^ /opt/smi/rus/bin/

muter-fin-install: tmp_fst/fin.fst tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/
	chmod a+x /opt/smi/fin/bin/*.fst

muter-install: muter-fin-install \
               muter-rus-install \
               muter-mrj-install \
               muter-mhr-install




#####
##### #valkstargets
#####

##
### #myvanalysers
##

tmp_fst/myv.fst:
	@echo "***********************"
	@echo "** Building myv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/myv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/myv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/imyv.fst

.PHONY: myv
myv: tmp_fst/myv.fst


##
### #mdfanalysers
##

tmp_fst/mdf.fst:
	@echo "***********************"
	@echo "** Building mdf FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/mdf/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/mdf.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/imdf.fst

.PHONY: mdf
mdf: tmp_fst/mdf.fst

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

.PHONY: valks-lexica
valks-lexica:  myv-lexicon mdf-lexicon

.PHONY: valks
valks: init myv mdf fin valks-lexica
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
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."


valks-fin-install: tmp_fst/fin.fst tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/
	chmod a+x /opt/smi/fin/bin/*.fst

valks-myv-install: tmp_fst/myv.fst tmp_ifst/imyv.fst
	mkdir -p /opt/smi/myv/bin/
	cp $^ /opt/smi/myv/bin/
	chmod a+x /opt/smi/myv/bin/*.fst

valks-mdf-install: tmp_fst/mdf.fst tmp_ifst/imdf.fst
	mkdir -p /opt/smi/mdf/bin/
	cp $^ /opt/smi/mdf/bin/
	chmod a+x /opt/smi/mdf/bin/*.fst

valks-install: valks-myv-install \
			   valks-mdf-install \
			   valks-fin-install


#####
##### #sanattargets
#####

##
### #oloanalysers
##

tmp_fst/olo.fst:
	@echo "***********************"
	@echo "** Building olo FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/olo/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/olo.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/iolo.fst

.PHONY: olo
olo: tmp_fst/olo.fst

##
### #livanalysers
##

tmp_fst/liv.fst:
	@echo "***********************"
	@echo "** Building liv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/liv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/liv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/iliv.fst

.PHONY: liv
liv: tmp_fst/liv.fst

##
### #fkvanalysers
##

tmp_fst/fkv.fst:
	@echo "***********************"
	@echo "** Building fkv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/fkv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/fkv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/ifkv.fst

.PHONY: fkv
fkv: tmp_fst/fkv.fst

##
### #izhanalysers
##

tmp_fst/izh.fst:
	@echo "***********************"
	@echo "** Building izh FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/izh/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/izh.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/iizh.fst

.PHONY: izh
izh: tmp_fst/izh.fst

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
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

sanat-olo-install: tmp_fst/olo.fst tmp_ifst/iolo.fst
	mkdir -p /opt/smi/olo/bin/
	cp $^ /opt/smi/olo/bin/
	chmod a+x /opt/smi/olo/bin/*.fst

sanat-liv-install: tmp_fst/liv.fst tmp_ifst/iliv.fst
	mkdir -p /opt/smi/liv/bin/
	cp $^ /opt/smi/liv/bin/
	chmod a+x /opt/smi/liv/bin/*.fst

sanat-izh-install: tmp_fst/izh.fst tmp_ifst/iizh.fst
	mkdir -p /opt/smi/izh/bin/
	cp $^ /opt/smi/izh/bin/
	chmod a+x /opt/smi/izh/bin/*.fst

sanat-fkv-install: tmp_fst/fkv.fst tmp_ifst/ifkv.fst
	mkdir -p /opt/smi/fkv/bin/
	cp $^ /opt/smi/fkv/bin/
	chmod a+x /opt/smi/fkv/bin/*.fst

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
# also, need to filter here
sme-nob.all.xml: $(GTHOME)/words/dicts/smenob/src/
	$(SAXON_SME_NOB) inDir=$^ | grep -v 'dict="no"' > $@

sme-fin.all.xml: $(GTHOME)/words/dicts/smefin/src/
	$(SAXON) inDir=$^ > $@

fin-sme.all.xml: $(GTHOME)/words/dicts/finsme/src/
	$(SAXON) inDir=$^ > $@

nob-sme.all.xml: $(GTHOME)/words/dicts/nobsme/
	mkdir -p tmp/nobsme/
	cp $^/src/* tmp/nobsme/
	cp $^/src_gt-only/* tmp/nobsme/
	cp $^/src_gt-fad_merged/* tmp/nobsme/
	$(SAXON) inDir=`pwd`/tmp/nobsme/ > $@
	rm -rf tmp/nobsme/

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
	chmod a+x /opt/smi/sme/bin/*.fst

##
### #smeanalysers
##


# NB not copying to tmp_fst/ or tmp_ifst/ because format is different for these.
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


tmp_fst/nob.fst:
	@echo "***********************"
	@echo "** Building nob FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/nob/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/nob.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/inob.fst

.PHONY: nob
nob: tmp_fst/nob.fst

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
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

sanit-fin-install: tmp_fst/fin.fst tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/
	chmod a+x /opt/smi/fin/bin/*.fst

sanit-nob-install: tmp_fst/nob.fst tmp_ifst/inob.fst
	mkdir -p /opt/smi/nob/bin/
	cp $^ /opt/smi/nob/bin/
	chmod a+x /opt/smi/nob/bin/*.fst

sanit-sme-install: n-sme.fst \
	               dict-isme-norm.fst \
	               some-n-sme.fst
	mkdir -p /opt/smi/sme/bin/
	cp $^ /opt/smi/sme/bin/
	chmod a+x /opt/smi/sme/bin/*.fst

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
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."

baakoeh-nob-install: tmp_fst/nob.fst tmp_ifst/inob.fst
	mkdir -p /opt/smi/nob/bin/
	cp $^ /opt/smi/nob/bin/
	chmod a+x /opt/smi/nob/bin/*.fst

baakoeh-sma-install: dict-sma.fst isma-dict.fst
	mkdir -p /opt/smi/sma/bin/
	cp $^ /opt/smi/sma/bin/
	chmod a+x /opt/smi/sma/bin/*.fst

baakoeh-install: baakoeh-sma-install \
				 baakoeh-nob-install


#####
##### #ereytargets
#####

##
### #somanalysers
##

som.fst:
isom.fst:
	@echo "***********************"
	@echo "** Building som FSTs **"
	@echo "***********************"
	@echo ""
	cd ~/somorph-priv.git/src/ ; \
	  make all ; \
	  cd .. ; \
	  cp bin/som.fst  $(TARGET_DIR)/tmp_fst/som.fst ; \
	  cp bin/isom.fst $(TARGET_DIR)/tmp_ifst/isom.fst

.PHONY: som
som: som.fst isom.fst

som.all.xml: ~/somorph-priv.git/xml/
	$(SAXON) inDir=$^ > $@

##
### #ereylexica
##

.PHONY: som-lexica
erey-lexica: som.all.xml

erey: init som fin erey-lexica
	@echo "*********************************"
	@echo "** Built targets for erey:     **"
	@echo "**    + erey lexicon           **"
	@echo "**    + som analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make erey-install"
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."


erey-som-install: tmp_fst/som.fst tmp_ifst/isom.fst
	mkdir -p /opt/smi/som/bin/
	cp $^ /opt/smi/som/bin/
	chmod a+x /opt/smi/som/bin/*.fst

erey-install: erey-som-install

#####
##### #guusaawtargets
#####

##
### #hdnanalysers
##

tmp_fst/hdn.fst:
	@echo "***********************"
	@echo "** Building hdn FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/hdn/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/hdn.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/ihdn.fst

.PHONY: hdn
hdn: tmp_fst/hdn.fst ihdn.fst

hdn.all.xml: $(GTHOME)/words/dicts/hdneng/src/*.xml
	@echo "**************************"
	@echo "** Building crk lexicon **"
	@echo "**************************"
	@echo ""
	$(SAXON) inDir=$(GTHOME)/words/dicts/hdneng/src/ > hdn.all.xml

##
### #guusaawlexica
##

.PHONY: hdn-lexica
guusaaw-lexica: hdn.all.xml

guusaaw: init hdn fin guusaaw-lexica
	@echo "*********************************"
	@echo "** Built targets for guusaaw:     **"
	@echo "**    + guusaaw lexicon           **"
	@echo "**    + hdn analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make guusaaw-install"
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."


guusaaw-hdn-install: tmp_fst/hdn.fst tmp_ifst/ihdn.fst
	mkdir -p /opt/smi/hdn/bin/
	cp $^ /opt/smi/hdn/bin/
	chmod a+x /opt/smi/hdn/bin/*.fst

guusaaw-install: guusaaw-hdn-install



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
	  cp src/analyser-gt-desc.xfst  $(TARGET_DIR)/tmp_fst/kpv.fst ; \
	  cp src/generator-gt-norm.xfst $(TARGET_DIR)/tmp_ifst/ikpv.fst

.PHONY: kpv
kpv: kpv.fst ikpv.fst

kpv-engfinrus.all.xml: $(GTHOME)/words/dicts/kom2X/src/
	$(SAXON) inDir=$^ > $@

##
### #kyvlexica
##

.PHONY: kpv-lexica
kyv-lexica: kpv-engfinrus.all.xml

kyv: init kpv fin kyv-lexica
	@echo "*********************************"
	@echo "** Built targets for kyv:      **"
	@echo "**    + kyv lexicon            **"
	@echo "**    + kpv analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make kyv-install"
	@echo "... or copy the fsts in tmp_fst/ and tmp_ifst/ to their right places."


kyv-fin-install: tmp_fst/fin.fst tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/
	chmod a+x /opt/smi/fin/bin/*.fst

kyv-kpv-install: tmp_fst/kpv.fst tmp_ifst/ikpv.fst
	mkdir -p /opt/smi/kpv/bin/
	cp $^ /opt/smi/kpv/bin/
	chmod a+x /opt/smi/kpv/bin/*.fst

kyv-install: kyv-kpv-install kyv-fin-install

# This one sets up dirnames, because can't get dirnames from inverse
SOURCES = tmp_fst/*.fst

.SUFFIXES: .fst
ISO: $(SOURCES)
	@echo $(foreach fst_file,    \
					$(SOURCES),  \
					$(fst_file)  \
		   )

# mkdir -p /opt/smi/$(notdir $(basename $<))/bin/
# cp $< /opt/smi/$(notdir $(basename $<))/bin/$(notdir $<)

iISO:
/opt/smi/%/bin/%.fst: tmp_ifst/%.fst
	@echo $<
	@printf "mkdir -p /opt/smi/$(basename $^)/bin"
	@printf "cp $< $^"

install-analysers: ISO iISO

#####
##### #Globaltargets
#####

INITTED := $(wildcard tmp_fst)

ifneq ($(strip $(INITTED)),)
init:
	@echo "Already initted..."
else
init:
	mkdir tmp_fst
	mkdir tmp_ifst
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
	@echo "To compile only the lexica, append -lexica to the target name:"
	@echo ""
	@echo " * make sanit-lexica"
	@echo " * make baakoeh-lexica"
	@echo " * make valks-lexica"
	@echo " * make vada-lexica"
	@echo " * make kyv-lexica"
	@echo ""
	@echo "NB! Make sure you have saxon9.jar in ~/lib/ !"

.PHONY: install
install: sanit-install baakoeh-install valks-install vada-install kyv-install
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
	 kyv \
	 muter
	@echo $(TARGET_DIR)

