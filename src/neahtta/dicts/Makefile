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

TIMESTAMP := $(shell date +%s)

define compile-lexicon =
	$(SAXON)
endef

#####
##### #Analyzers used in nearly everything
#####

##
### #finanalysers
##

/tmp/tmp_fst/fin.fst:
	@echo "***********************"
	@echo "** Building fin FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/fin/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/fin.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/ifin.fst

.PHONY: fin
fin: /tmp/tmp_fst/fin.fst /tmp/tmp_ifst/ifin.fst

rm-fin: 
	rm -rf /tmp/tmp_fst/fin.fst /tmp/tmp_ifst/ifin.fst


# TODO: actually in st

##
### #rusanalysers
##

/tmp/tmp_fst/rus.fst:
	@echo "***********************"
	@echo "** Building rus FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/rus/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/rus.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/irus.fst

.PHONY: rus
rus: /tmp/tmp_fst/rus.fst /tmp/tmp_ifst/irus.fst

rm-rus: 
	rm -rf /tmp/tmp_fst/rus.fst /tmp/tmp_ifst/irus.fst




#####
##### #guusaawtargets
#####

##
### #hdnanalysers
##

/tmp/tmp_fst/hdn.fst:
	@echo "***********************"
	@echo "** Building hdn FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/hdn/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/hdn.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/ihdn.fst

.PHONY: hdn
hdn: /tmp/tmp_fst/hdn.fst /tmp/tmp_ifst/ihdn.fst

rm-hdn: 
	rm -rf /tmp/tmp_fst/hdn.fst /tmp/tmp_ifst/ihdn.fst


##
### #guusaawlexicon
##

hdn.all.xml: $(GTHOME)/words/dicts/hdneng/src/*.xml
	@echo "**************************"
	@echo "** Building hdn lexicon **"
	@echo "**************************"
	@echo ""
	$(SAXON) inDir=$(GTHOME)/words/dicts/hdneng/src/ > hdn.all.xml

.PHONY: guusaaw-lexicon
guusaaw-lexica: hdn.all.xml

rm-guusaaw-lexica: 
	@rm -rf hdn.all.xml

.PHONY: guusaaw
guusaaw: init hdn eng guusaaw-lexica
	@echo "*************************************"
	@echo "** Built targets for guusaaw:      **"
	@echo "**    + hdn lexicon                **"
	@echo "**    + hdn analysers              **"
	@echo "*************************************"
	@echo "**   (hdn = Northern Haida)        **"
	@echo "*************************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make guusaaw-install"
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

guusaaw-hdn-install: /tmp/tmp_fst/hdn.fst /tmp/tmp_ifst/ihdn.fst
	mkdir -p /opt/smi/hdn/bin/
	cp $^ /opt/smi/hdn/bin/

guusaaw-install: guusaaw-hdn-install




#####
##### #pikiskwewinatargets
#####

##
### #crkanalysers
##

/tmp/tmp_fst/crk.fst:
	@echo "***********************"
	@echo "** Building crk FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/crk/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/crk.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/icrk.fst

.PHONY: crk
crk: /tmp/tmp_fst/crk.fst /tmp/tmp_ifst/icrk.fst

rm-crk: 
	rm -rf /tmp/tmp_fst/crk.fst /tmp/tmp_ifst/icrk.fst


##
### #pikiskwewinalexicon
##

crk-all.xml: $(GTHOME)/words/dicts/crkeng/src/*.xml
	@echo "**************************"
	@echo "** Building crk lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$(GTHOME)/words/dicts/crkeng/src/ > crk-all.xml

.PHONY: crk-lexicon
pikiskwewina-lexica: crk-all.xml

rm-pikiskwewina-lexica:
	@rm -rf crk-all.xml

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

pikiskwewina-crk-install: /tmp/tmp_fst/crk.fst /tmp/tmp_ifst/icrk.fst
	mkdir -p /opt/smi/crk/bin/
	cp $^ /opt/smi/crk/bin/

pikiskwewina-install: pikiskwewina-crk-install


#####
##### #saantargets
#####

##
### #smsanalysers
##

/tmp/tmp_fst/sms.fst:
	@echo "***********************"
	@echo "** Building sms FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/sms/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/sms.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/isms.fst

.PHONY: sms
sms: /tmp/tmp_fst/sms.fst /tmp/tmp_ifst/isms.fst

rm-sms: 
	rm -rf /tmp/tmp_fst/sms.fst /tmp/tmp_ifst/isms.fst


##
### #saanlexicon
##

sms-all.xml: $(GTHOME)/langs/sms/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building sms lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir sms
	cp $^ sms/
	$(SAXON) inDir=$(pwd)/sms/ > sms-all.xml
	rm -rf sms/

.PHONY: sms-lexicon
saan-lexica: sms-all.xml

rm-saan-lexica: 
	@rm -rf sms-all.xml

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

saan-sms-install: /tmp/tmp_fst/sms.fst /tmp/tmp_ifst/isms.fst
	mkdir -p /opt/smi/sms/bin/
	cp $^ /opt/smi/sms/bin/

saan-install: saan-sms-install


#####
##### #vadatargets
#####

##
### #yrkanalysers
##

/tmp/tmp_fst/yrk.fst:
	@echo "***********************"
	@echo "** Building yrk FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/yrk/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/yrk.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/iyrk.fst

.PHONY: yrk
yrk: /tmp/tmp_fst/yrk.fst /tmp/tmp_ifst/iyrk.fst

rm-yrk: 
	rm -rf /tmp/tmp_fst/yrk.fst /tmp/tmp_ifst/iyrk.fst


##
### #vadalexicon
##

yrk-all.xml: $(GTHOME)/langs/yrk/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building yrk lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir yrk
	cp $^ yrk/
	$(SAXON) inDir=$(pwd)/yrk/ > yrk-all.xml
	rm -rf yrk/

.PHONY: yrk-lexicon
vada-lexica: yrk-all.xml

rm-vada-lexica: 
	@rm -rf yrk-all.xml

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

vada-yrk-install: /tmp/tmp_fst/yrk.fst /tmp/tmp_ifst/iyrk.fst
	mkdir -p /opt/smi/yrk/bin/
	cp $^ /opt/smi/yrk/bin/

vada-install: vada-yrk-install

#####
##### #mutertargets
#####

##
### #mhranalysers
##

/tmp/tmp_fst/mhr.fst:
	@echo "***********************"
	@echo "** Building mhr FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/mhr/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/mhr.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/imhr.fst

##
### #mrjanalysers
##

/tmp/tmp_fst/mrj.fst:
	@echo "***********************"
	@echo "** Building mrj FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/mrj/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/mrj.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/imrj.fst

.PHONY: mhr
mhr: /tmp/tmp_fst/mhr.fst /tmp/tmp_ifst/imhr.fst

rm-mhr: 
	rm -rf /tmp/tmp_fst/mhr.fst /tmp/tmp_ifst/imhr.fst


.PHONY: mrj
mrj: /tmp/tmp_fst/mrj.fst /tmp/tmp_ifst/imrj.fst

rm-mrj: 
	rm -rf /tmp/tmp_fst/mrj.fst /tmp/tmp_ifst/imrj.fst


##
### #muterlexicon
##


mrj-all.xml: $(GTHOME)/langs/mrj/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building mrj lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir mrj
	cp $^ mrj/
	$(SAXON) inDir=$(pwd)/mrj/ > mrj-all.xml
	rm -rf mrj/

mhr-all.xml: $(GTHOME)/langs/mhr/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building mhr lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir mhr
	cp $^ mhr/
	$(SAXON) inDir=$(pwd)/mhr/ > mhr-all.xml
	rm -rf mhr/

.PHONY: muter-lexicon
muter-lexica: mhr-all.xml mrj-all.xml

rm-muter-lexica: 
	@rm -rf mhr-all.xml mrj-all.xml

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

muter-mhr-install: /tmp/tmp_fst/mhr.fst /tmp/tmp_ifst/imhr.fst
	mkdir -p /opt/smi/mhr/bin/
	cp $^ /opt/smi/mhr/bin/

muter-mrj-install: /tmp/tmp_fst/mrj.fst /tmp/tmp_ifst/imrj.fst
	mkdir -p /opt/smi/mrj/bin/
	cp $^ /opt/smi/mrj/bin/

# muter-rus-install: /tmp/tmp_fst/rus.fst /tmp/tmp_ifst/irus.fst
muter-rus-install:
	@echo "TODO: rus"
	# mkdir -p /opt/smi/rus/bin/
	# cp $^ /opt/smi/rus/bin/

muter-fin-install: /tmp/tmp_fst/fin.fst /tmp/tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/

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

/tmp/tmp_fst/myv.fst:
	@echo "***********************"
	@echo "** Building myv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/myv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/myv.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/imyv.fst

.PHONY: myv
myv: /tmp/tmp_fst/myv.fst /tmp/tmp_ifst/imyv.fst

rm-myv: 
	rm -rf /tmp/tmp_fst/myv.fst /tmp/tmp_ifst/imyv.fst



##
### #mdfanalysers
##

/tmp/tmp_fst/mdf.fst:
	@echo "***********************"
	@echo "** Building mdf FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/mdf/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/mdf.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/imdf.fst

.PHONY: mdf
mdf: /tmp/tmp_fst/mdf.fst /tmp/tmp_ifst/imdf.fst

rm-mdf: 
	rm -rf /tmp/tmp_fst/mdf.fst /tmp/tmp_ifst/imdf.fst


myv-all.xml: $(GTHOME)/langs/myv/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building myv lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir myv
	cp $^ myv/
	$(SAXON) inDir=$(pwd)/myv/ > myv-all.xml
	rm -rf myv/

mdf-all.xml: $(GTHOME)/langs/mdf/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building mdf lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir mdf
	cp $^ mdf/
	$(SAXON) inDir=$(pwd)/mdf/ > mdf-all.xml
	rm -rf mdf/

valks-lexica:  myv-all.xml mdf-all.xml

rm-valks-lexica:
	rm -rf myv-all.xml mdf-all.xml	

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."


valks-fin-install: /tmp/tmp_fst/fin.fst /tmp/tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/

valks-myv-install: /tmp/tmp_fst/myv.fst /tmp/tmp_ifst/imyv.fst
	mkdir -p /opt/smi/myv/bin/
	cp $^ /opt/smi/myv/bin/

valks-mdf-install: /tmp/tmp_fst/mdf.fst /tmp/tmp_ifst/imdf.fst
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

/tmp/tmp_fst/olo.fst:
	@echo "***********************"
	@echo "** Building olo FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/olo/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/olo.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/iolo.fst

.PHONY: olo
olo: /tmp/tmp_fst/olo.fst /tmp/tmp_ifst/iolo.fst

rm-olo: 
	rm -rf /tmp/tmp_fst/olo.fst /tmp/tmp_ifst/iolo.fst


##
### #livanalysers
##

/tmp/tmp_fst/liv.fst:
	@echo "***********************"
	@echo "** Building liv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/liv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/liv.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/iliv.fst

.PHONY: liv
liv: /tmp/tmp_fst/liv.fst /tmp/tmp_ifst/iliv.fst

rm-liv: 
	rm -rf /tmp/tmp_fst/liv.fst /tmp/tmp_ifst/iliv.fst


##
### #fkvanalysers
##

/tmp/tmp_fst/fkv.fst:
	@echo "***********************"
	@echo "** Building fkv FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/fkv/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/fkv.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/ifkv.fst

.PHONY: fkv
fkv: /tmp/tmp_fst/fkv.fst /tmp/tmp_ifst/ifkv.fst

rm-fkv: 
	rm -rf /tmp/tmp_fst/fkv.fst /tmp/tmp_ifst/ifkv.fst


##
### #izhanalysers
##

/tmp/tmp_fst/izh.fst:
	@echo "***********************"
	@echo "** Building izh FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/izh/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/izh.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/iizh.fst

.PHONY: izh
izh: /tmp/tmp_fst/izh.fst /tmp/tmp_ifst/iizh.fst

rm-izh: 
	rm -rf /tmp/tmp_fst/izh.fst /tmp/tmp_ifst/iizh.fst


##
### #sanatlexica
##

olo-fin.xml: $(GTHOME)/langs/olo/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building olo lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir olo
	cp $^ olo/
	$(SAXON) inDir=$(pwd)/olo/ > $@
	rm -rf olo/

fkv-nob.xml: $(GTHOME)/words/dicts/fkvnob/src/
	@echo "**************************"
	@echo "** Building fkv lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

# NOTE: some temporary fixes to add usage to everything, and include <lg>
# node
nob-fkv.xml: $(GTHOME)/words/dicts/nobfkv/src/
	@echo "******************************"
	@echo "** Building nob-fkv lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@.tmp
	cat $@.tmp | sed 's/<e>/<e usage="vd">/g' | \
				 sed 's/  <l /  <lg><l /g'    | \
				 sed 's/<\/l>/<\/l><\/lg>/g'  | \
				 xmllint --format - \
		   	 	 > $@
	rm $@.tmp

liv.all.xml: $(GTHOME)/langs/liv/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building liv lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir liv
	cp $^ liv/
	$(SAXON) inDir=$(pwd)/liv/ > $@
	rm -rf liv/

izh-fin.xml: $(GTHOME)/langs/izh/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building izh lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
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

rm-sanat-lexica: 
	@rm -rf olo-fin.xml liv.all.xml izh-fin.xml fkv-nob.xml nob-fkv.xml

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

sanat-olo-install: /tmp/tmp_fst/olo.fst /tmp/tmp_ifst/iolo.fst
	mkdir -p /opt/smi/olo/bin/
	cp $^ /opt/smi/olo/bin/

sanat-liv-install: /tmp/tmp_fst/liv.fst /tmp/tmp_ifst/iliv.fst
	mkdir -p /opt/smi/liv/bin/
	cp $^ /opt/smi/liv/bin/

sanat-izh-install: /tmp/tmp_fst/izh.fst /tmp/tmp_ifst/iizh.fst
	mkdir -p /opt/smi/izh/bin/
	cp $^ /opt/smi/izh/bin/

sanat-fkv-install: /tmp/tmp_fst/fkv.fst /tmp/tmp_ifst/ifkv.fst
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
# also, need to filter here
sme-nob.all.xml: $(GTHOME)/words/dicts/smenob/src/
	@echo "******************************"
	@echo "** Building sme-nob lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON_SME_NOB) inDir=$^ | grep -v 'dict="no"' > $@

sme-fin.all.xml: $(GTHOME)/words/dicts/smefin/src/
	@echo "******************************"
	@echo "** Building sme-fin lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

fin-sme.all.xml: $(GTHOME)/words/dicts/finsme/src/
	@echo "******************************"
	@echo "** Building fin-sme lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

nob-sme.all.xml: $(GTHOME)/words/dicts/nobsme/ \
				 $(GTHOME)/words/dicts/nobsme/src/*.xml \
				 $(GTHOME)/words/dicts/nobsme/src_gt-only/*.xml \
				 $(GTHOME)/words/dicts/nobsme/src_gt-fad_merged/*.xml
	@echo "******************************"
	@echo "** Building nob-sme lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	mkdir -p tmp/nobsme/
	cp $</src/* tmp/nobsme/
	cp $</src_gt-only/* tmp/nobsme/
	cp $</src_gt-fad_merged/* tmp/nobsme/
	$(SAXON) inDir=`pwd`/tmp/nobsme/ > $@
	rm -rf tmp/nobsme/

.PHONY: sanit-lexica
sanit-lexica: fin-sme.all.xml \
			  nob-sme.all.xml \
			  sme-fin.all.xml \
			  sme-nob.all.xml

rm-sanit-lexica:
	@rm -rf fin-sme.all.xml nob-sme.all.xml sme-fin.all.xml sme-nob.all.xml

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


# NB not copying to /tmp/tmp_fst/ or /tmp/tmp_ifst/ because format is different for these.
/tmp/misc_fst/n-sme.fst:
/tmp/misc_fst/dict-isme-norm.fst:
/tmp/misc_fst/some-n-sme.fst:
	@echo "***********************"
	@echo "** Building sme FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/gt/ ; \
	  make TARGET=sme ; \
	  cp sme/bin/n-sme.fst  /tmp/misc_fst/n-sme.fst ; \
	  cp sme/bin/some-n-sme.fst  /tmp/misc_fst/some-n-sme.fst ; \
	  cp sme/bin/dict-isme-norm.fst /tmp/misc_fst/dict-isme-norm.fst


/tmp/tmp_fst/nob.fst:
	@echo "***********************"
	@echo "** Building nob FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/nob/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make  ; \
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/nob.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/inob.fst

.PHONY: nob
nob: /tmp/tmp_fst/nob.fst /tmp/tmp_ifst/inob.fst

rm-nob:
	rm -rf /tmp/tmp_fst/nob.fst /tmp/tmp_ifst/inob.fst


.PHONY: sme
sme: /tmp/misc_fst/n-sme.fst \
	 /tmp/misc_fst/dict-isme-norm.fst \
	 /tmp/misc_fst/some-n-sme.fst

rm-sme:
	rm -rf /tmp/misc_fst/n-sme.fst /tmp/misc_fst/dict-isme-norm.fst /tmp/misc_fst/some-n-sme.fst

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

sanit-fin-install: /tmp/tmp_fst/fin.fst /tmp/tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/

sanit-nob-install: /tmp/tmp_fst/nob.fst /tmp/tmp_ifst/inob.fst
	mkdir -p /opt/smi/nob/bin/
	cp $^ /opt/smi/nob/bin/

sanit-sme-install: /tmp/misc_fst/n-sme.fst \
	               /tmp/misc_fst/dict-isme-norm.fst \
	               /tmp/misc_fst/some-n-sme.fst
	mkdir -p /opt/smi/sme/bin/
	cp $^ /opt/smi/sme/bin/

sanit-install: sanit-nob-install sanit-sme-install sanit-fin-install


#####
##### #baakoehtargets
#####

##
### #smaanalysers
##

/tmp/misc_fst/dict-sma.fst:
/tmp/misc_fst/isma-dict.fst:
	@echo "***********************"
	@echo "** Building sma FSTs **"
	@echo "***********************"
	@echo ""
	cd $(GTHOME)/langs/sma/ ; \
	  ./autogen.sh ; \
	  ./configure  ; \
	  make ; \
	  cp src/analyser-dict-gt-desc.xfst  /tmp/misc_fst/dict-sma.fst ; \
	  cp src/generator-dict-gt-norm.xfst /tmp/misc_fst/isma-dict.fst

.PHONY: sma
sma: /tmp/misc_fst/dict-sma.fst /tmp/misc_fst/isma-dict.fst

rm-sma:
	rm -rf /tmp/misc_fst/dict-sma.fst /tmp/misc_fst/isma-dict.fst


##
### #baakoehlexica
##

# NB: these are more similar to sme lexicon, but FST differs.
sma-nob.all.xml: $(GTHOME)/words/dicts/smanob/src/
	@echo "******************************"
	@echo "** Building sma-nob lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

nob-sma.all.xml: $(GTHOME)/words/dicts/nobsma/src/
	@echo "******************************"
	@echo "** Building nob-sma lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

baakoeh-lexica: sma-nob.all.xml \
				nob-sma.all.xml

rm-baakoeh-lexica: 
	@rm -rf sma-nob.all.xml nob-sma.all.xml

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

baakoeh-nob-install: /tmp/tmp_fst/nob.fst /tmp/tmp_ifst/inob.fst
	mkdir -p /opt/smi/nob/bin/
	cp $^ /opt/smi/nob/bin/

baakoeh-sma-install: /tmp/misc_fst/dict-sma.fst /tmp/misc_fst/isma-dict.fst
	mkdir -p /opt/smi/sma/bin/
	cp $^ /opt/smi/sma/bin/

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
	  cp bin/som.fst  /tmp/tmp_fst/som.fst ; \
	  cp bin/isom.fst /tmp/tmp_ifst/isom.fst

.PHONY: som
som: som.fst isom.fst

rm-som:
	rm -rf som.fst isom.fst


som.all.xml: ~/somorph-priv.git/xml/
	$(SAXON) inDir=$^ > $@

##
### #ereylexica
##

.PHONY: som-lexica
erey-lexica: som.all.xml

rm-erey-lexica:
	@rm -rf som.all.xml

erey: init som fin erey-lexica
	@echo "*********************************"
	@echo "** Built targets for erey:     **"
	@echo "**    + erey lexicon           **"
	@echo "**    + som analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make erey-install"
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."


erey-som-install: /tmp/tmp_fst/som.fst /tmp/tmp_ifst/isom.fst
	mkdir -p /opt/smi/som/bin/
	cp $^ /opt/smi/som/bin/

erey-install: erey-som-install

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
	  cp src/analyser-gt-desc.xfst  /tmp/tmp_fst/kpv.fst ; \
	  cp src/generator-gt-norm.xfst /tmp/tmp_ifst/ikpv.fst

.PHONY: kpv
kpv: kpv.fst ikpv.fst

rm-kpv:
	rm -rf kpv.fst ikpv.fst

kpv-engfinrus.all.xml: $(GTHOME)/words/dicts/kom2X/src/
	@echo "**************************"
	@echo "** Building kpv lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

##
### #kyvlexica
##

.PHONY: kyv-lexica
kyv-lexica: kpv-engfinrus.all.xml

rm-kyv-lexica:
	@rm -rf kpv-engfinrus.all.xml

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
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."


kyv-fin-install: /tmp/tmp_fst/fin.fst /tmp/tmp_ifst/ifin.fst
	mkdir -p /opt/smi/fin/bin/
	cp $^ /opt/smi/fin/bin/

kyv-kpv-install: /tmp/tmp_fst/kpv.fst /tmp/tmp_ifst/ikpv.fst
	mkdir -p /opt/smi/kpv/bin/
	cp $^ /opt/smi/kpv/bin/

kyv-install: kyv-kpv-install kyv-fin-install

# This one sets up dirnames, because can't get dirnames from inverse
SOURCES = /tmp/tmp_fst/*.fst

.SUFFIXES: .fst
ISO: $(SOURCES)
	@echo $(foreach fst_file,    \
					$(SOURCES),  \
					$(fst_file)  \
		   )

# mkdir -p /opt/smi/$(notdir $(basename $<))/bin/
# cp $< /opt/smi/$(notdir $(basename $<))/bin/$(notdir $<)

iISO:
/opt/smi/%/bin/%.fst: /tmp/tmp_ifst/%.fst
	@echo $<
	@printf "mkdir -p /opt/smi/$(basename $^)/bin"
	@printf "cp $< $^"

install-analysers: ISO iISO

#####
##### #Globaltargets
#####

INITTED := $(wildcard /tmp/tmp_fst)

ifneq ($(strip $(INITTED)),)
init:
	@echo "Already initted..."
else
init:
	mkdir /tmp/tmp_fst
	mkdir /tmp/tmp_ifst
	mkdir /tmp/misc_fst
	@echo ""
	@echo ""
	@echo "Is saxon9.lib in the path somewhere?"
	@echo ""
	@echo ""
endif

clean:
	rm -rf /tmp/tmp_fst /tmp/tmp_ifst /tmp/misc_fst

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

