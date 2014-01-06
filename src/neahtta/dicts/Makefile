#######################
##                   ##
## Table of Contents ##
##                   ##
#######################

# TODO: when templates are updated, not everything is noticed in make
# process for main/langs/, so it might be necessary to do a distclean,
# and reautogen from time to time

# Some helpful tags for jumping around

###         #guusaawtargets
###         
###         #pikiskwewinatargets
###         
###         #saantargets
###         
###         #vadatargets
###         
###         #valkstargets
###         
###         #mutertargets
###         
###         #sanattargets
###         
###         #sanittargets
###          #smeanalysers
###          #sanitlexica
###         
###         #baakoehtargets
###         
###         #kyvtargets
###         
###         #ereytargets
###         
###         #Globaltargets

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

# This is a generalized target to compile a list of languages defined in a
# target-specific variable for each NDS instance (valks, sanit, etc.). Note,
# this only works with new-infra language (~/gtsvn/langs/), so languages
# outside will need to have their own build target.
#
# To use this on any given target, set the variable, and call this as a
# dependency
#
# .PHONY: dict_project_name
# dict_project_name: GT_COMPILE_LANGS := iso1 iso2
# dict_project_name: dict_project_name-lexica compile_langs_fsts
# 	@echo "Usual target stuff goes here..." 
#
# Or just see one of the languages below and copy...

compile_langs_fsts: $(foreach lang, $(GT_COMPILE_LANGS), langs/$(lang)/src/analyser-gt-desc.xfst)
compile_langs_fsts: $(langs)
	@echo $*
	@echo "***********************"
	@echo "** Building $(GT_COMPILE_LANGS) FSTs **"
	@echo "***********************"
	@echo ""
	mkdir -p /tmp/tmp_fst/
	mkdir -p /tmp/tmp_ifst/
	mkdir -p /tmp/misc_fst/
	for ll in $(GT_COMPILE_LANGS) ; do \
 		if ! test -e "$(GTHOME)/langs/$$ll/src/Makefile" ; then \
 			cd $(GTHOME)/langs/$$ll ; ./autogen.sh ; ./configure --enable-dicts ; \
 		fi ; \
 		cd $(GTHOME)/langs/$$ll ; make ; \
	    cp $(GTHOME)/langs/$$ll/src/analyser-dict-gt-desc.xfst  /tmp/tmp_fst/dict-$$ll.fst ; \
	    cp $(GTHOME)/langs/$$ll/src/generator-gt-norm.xfst /tmp/tmp_ifst/dict-i$$ll-norm.fst ; \
		cp $(GTHOME)/langs/$$ll/src/analyser-dict-gt-desc-mobile.xfst  /tmp/misc_fst/some-$$ll.fst 2>/dev/null || : ; \
	done 

install_langs_fsts: $(foreach lang, $(GT_COMPILE_LANGS), langs/$(lang)/src/analyser-gt-desc.xfst)
install_langs_fsts: $(langs)
	@echo $*
	@echo "***********************"
	@echo "** Copying to target for: $(GT_COMPILE_LANGS) **"
	@echo "***********************"
	@echo ""
	for ll in $(GT_COMPILE_LANGS) ; do \
		mkdir -p /opt/smi/$$ll/bin/ ; \
		cp /tmp/tmp_fst/dict-$$ll.fst /opt/smi/$$ll/bin/ ; \
		cp /tmp/tmp_ifst/dict-i$$ll-norm.fst /opt/smi/$$ll/bin/ ; \
		cp /tmp/misc_fst/some-$$ll.fst /opt/smi/$$ll/bin/ 2>/dev/null || : ; \
	done 

#####
##### #guusaawtargets
#####

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

.PHONY: guusaaw-install
guusaaw-install: GT_COMPILE_LANGS := hdn
guusaaw-install: guusaaw-hdn-install

.PHONY: guusaaw
guusaaw: GT_COMPILE_LANGS := hdn
guusaaw: guusaaw-lexica compile_langs_fsts
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


#####
##### #pikiskwewinatargets
#####

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

.PHONY: rm-pikiswkewina-lexica
rm-pikiskwewina-lexica:
	@rm -rf crk-all.xml


.PHONY: pikiskwewina-install
pikiskwewina-install: GT_COMPILE_LANGS := crk
pikiskwewina-install: install_langs_fsts

.PHONY: pikiskwewina
pikiskwewina: GT_COMPILE_LANGS := crk
pikiskwewina: pikiskwewina-lexica compile_langs_fsts
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

#####
##### #saantargets
#####

sms-all.xml: $(GTHOME)/words/dicts/sms2X/src/cmn/*.xml
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

.PHONY: saan-install
saan-install: GT_COMPILE_LANGS := sms fin
saan-install: install_langs_fsts 

.PHONY: saan
saan: GT_COMPILE_LANGS := sms fin
saan: compile_langs_fsts saan-lexica
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

#####
##### #vadatargets
#####

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

.PHONY: vada-install
vada-install: GT_COMPILE_LANGS := yrk fin
vada-install: install_langs_fsts 

.PHONY: vada
vada: GT_COMPILE_LANGS := yrk fin
vada: vada-lexica compile_langs_fsts
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

#####
##### #mutertargets
#####

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

.PHONY: muter-install
muter-install: GT_COMPILE_LANGS := mrj mhr fin 
muter-install: install_langs_fsts

.PHONY: muter
muter: GT_COMPILE_LANGS := mrj mhr fin rus
muter: muter-lexicon compile_langs_fsts
	@echo "*********************************"
	@echo "** Built targets for muter:     **"
	@echo "**    + mhr lexicon            **"
	@echo "**    + mrj lexicon            **"
	@echo "**    + mhr analysers          **"
	@echo "**    + mrj analysers          **"
	@echo "**    + rus analysers          **"
	@echo "**    + fin analysers          **"
	@echo "*********************************"
	@echo "**   (mhr = Eastern Mari)      **"
	@echo "**   (mrj = Western Mari)      **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make muter-install"
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

#####
##### #valkstargets
#####

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

.PHONY: valks-install
valks-install: GT_COMPILE_LANGS := fin myv mdf
valks-install: install_langs_fsts 

.PHONY: valks
valks: GT_COMPILE_LANGS := fin myv mdf
valks: valks-lexica compile_langs_fsts
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

#####
##### #sanattargets
#####

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

.PHONY: sanat-install
sanat-install: GT_COMPILE_LANGS := olo liv izh fkv
sanat-install: install_langs_fsts 

.PHONY: sanat
sanat: GT_COMPILE_LANGS := olo izh liv fin fkv
sanat: sanat-lexica compile_langs_fsts
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
	-@rm -rf tmp/nobsme/
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
sme-install: dict-sme.fst dict-isme-norm.fst some-n-sme.fst
	cp $^ /opt/smi/sme/bin/

##
### #smeanalysers
##

# copy above and use new files from langs infra.

/tmp/misc_fst/dict-sme.fst:
/tmp/misc_fst/dict-isme-norm.fst:
/tmp/misc_fst/some-sme.fst:
	@echo "***********************"
	@echo "** Building sme FSTs **"
	@echo "***********************"
	@echo ""
	-@mkdir -p /tmp/misc_fst/
	if ! test -e "$(GTHOME)/langs/sme/Makefile" ; then \
		cd $(GTHOME)/langs/sme ; ./autogen.sh ; ./configure --enable-dicts ; \
	fi ; \
	cd $(GTHOME)/langs/sme ; make ; \
	cp $(GTHOME)/langs/sme/src/analyser-dict-gt-desc.xfst  /tmp/misc_fst/dict-sme.fst ; \
	cp $(GTHOME)/langs/sme/src/analyser-dict-gt-desc-mobile.xfst  /tmp/misc_fst/some-sme.fst ; \
	cp $(GTHOME)/langs/sme/src/generator-dict-gt-norm.xfst /tmp/misc_fst/dict-isme-norm.fst ; \

.PHONY: sme
sme: /tmp/misc_fst/dict-sme.fst \
	 /tmp/misc_fst/dict-isme-norm.fst \
	 /tmp/misc_fst/some-sme.fst

rm-sme:
	rm -rf /tmp/misc_fst/dict-sme.fst /tmp/misc_fst/dict-isme-norm.fst /tmp/misc_fst/some-n-sme.fst

# NB: sme has own needs
.PHONY: sanit-install
sanit-install: GT_COMPILE_LANGS := fin nob
sanit-install: sanit-sme-install install_langs_fsts

# NB: sme has its own path, is not included in GT_COMPILE_LANGS because
# it isn't in main/langs/ yet.
.PHONY: sanit
sanit: GT_COMPILE_LANGS := fin nob
sanit: sme sanit-lexica compile_langs_fsts
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

sanit-sme-install: /tmp/misc_fst/dict-sme.fst \
	               /tmp/misc_fst/dict-isme-norm.fst \
	               /tmp/misc_fst/some-sme.fst
	mkdir -p /opt/smi/sme/bin/
	cp $^ /opt/smi/sme/bin/

#####
##### #baakoehtargets
#####

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

.PHONY: baakoeh-install
baakoeh-install: GT_COMPILE_LANGS := sma nob
baakoeh-install: install_langs_fsts 

.PHONY: baakoeh
baakoeh: GT_COMPILE_LANGS := sma nob
baakoeh: baakoeh-lexica compile_langs_fsts
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

#####
##### #ereytargets
#####

som.all.xml: ~/somorph-priv.git/xml/
	$(SAXON) inDir=$^ > $@

##
### #ereylexica
##

.PHONY: som-lexica
erey-lexica: som.all.xml

rm-erey-lexica:
	@rm -rf som.all.xml

.PHONY: erey-install
erey-install: GT_COMPILE_LANGS := som fin
erey-install: erey install_langs_fsts 

.PHONY: erey
erey: GT_COMPILE_LANGS := som fin
erey: erey-lexica compile_langs_fsts
	@echo "*********************************"
	@echo "** Built targets for erey:     **"
	@echo "**    + erey lexicon           **"
	@echo "**    + som analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make erey-install"
	@echo "... or copy the fsts in /tmp/tmp_fst/ and /tmp/tmp_ifst/ to their right places."

#####
##### #kyvtargets
#####

kpv-engfinrus.all.xml: $(GTHOME)/words/dicts/kom2X/src/
	@echo "**************************"
	@echo "** Building kpv lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

udm-all.xml: $(GTHOME)/langs/udm/src/morphology/stems/*.xml
	@echo "**************************"
	@echo "** Building udm lexicon **"
	@echo "**************************"
	@echo "** Backup made (.bak)   **"
	@echo "**************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir udm
	cp $^ udm/
	$(SAXON) inDir=$(pwd)/udm/ > udm-all.xml
	rm -rf udm/

.PHONY: kyv-lexica
kyv-lexica: kpv-engfinrus.all.xml udm-all.xml

rm-kyv-lexica:
	@rm -rf kpv-engfinrus.all.xml udm-all.xml

.PHONY: copy_molotsov
copy_molotsov: $(GTHOME)/langs/kpv/src/analyser-dict-gt-desc-molotsov.xfst
	cp $^ /opt/smi/kpv/bin/dict-kpv-molotsov.fst

.PHONY: kyv-install
kyv-install: GT_COMPILE_LANGS := kpv fin udm
kyv-install: install_langs_fsts copy_molotsov

.PHONY: kyv
kyv: GT_COMPILE_LANGS := kpv fin udm
kyv: kyv-lexica compile_langs_fsts
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

#####
##### #Globaltargets
#####

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
	@echo "To install FSTs to /opt/smi/ paths:"
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
all: vada  \
	 valks \
	 sanat \
	 sanit \
	 baakoeh \
	 kyv \
	 muter
	@echo $(TARGET_DIR)

