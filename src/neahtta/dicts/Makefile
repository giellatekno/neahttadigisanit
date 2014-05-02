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
#	@echo "Usual target stuff goes here..." 
#
# Or just see one of the languages below and copy...

compile_langs_fsts: $(foreach lang, $(GT_COMPILE_LANGS), langs/$(lang)/src/analyser-gt-desc.xfst)
compile_langs_fsts: $(langs)
	@echo $*
	@echo "***********************"
	@echo "** Building $(GT_COMPILE_LANGS) FSTs **"
	@echo "***********************"
	@echo ""
	for ll in $(GT_COMPILE_LANGS) ; do \
		if ! test -e "$(GTHOME)/langs/$$ll/src/Makefile" ; then \
			cd $(GTHOME)/langs/$$ll ; ./autogen.sh ; ./configure --enable-dicts ; \
		fi ; \
		cd $(GTHOME)/langs/$$ll ; make ; \
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
		cp $(GTHOME)/langs/$$ll/src/analyser-dict-gt-desc.xfst  /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/langs/$$ll/src/generator-dict-gt-norm.xfst /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/langs/$$ll/src/analyser-dict-gt-desc-mobile.xfst  /opt/smi/$$ll/bin/ 2>/dev/null || : ; \
	done 

.PHONY: compile_langs_lexicon
compile_langs_lexicon: $(LEX_COMPILE_LANGS)
compile_langs_lexicon:
	@echo $*
	@echo "***********************"
	@echo "** Copying to target for: $(LEX_COMPILE_LANGS) **"
	@echo "***********************"
	@echo ""
	for ll in $(LEX_COMPILE_LANGS) ; do \
		echo " * Compiling langs lexica for $$ll" ; \
		if ! test -e "$$ll-all.xml " ; then \
			echo " * Backing up to $$ll-all.xml.$(shell date +%s).bak"  ; \
			cp -R $$ll-all.xml $$ll-all.xml.$(shell date +%s).bak ; \
		fi ; \
		$(SAXON) inDir=$(GTHOME)/langs/$$ll/src/morphology/stems/ > $$ll-all.xml ; \
		echo " * Compiling resulted in: " ; \
		wc -l $$ll-all.xml ; \
	done

.PHONY: compile_words_dicts_lexicon
compile_words_dicts_lexicon: $(LEX_COMPILE_WORDS_DICTS)
compile_words_dicts_lexicon:
	@echo "***********************"
	@echo "** Copying to target for: $(LEX_COMPILE_WORDS_DICTS) **"
	@echo "***********************"
	@echo ""
	for ll in $(LEX_COMPILE_WORDS_DICTS) ; do \
		echo " * Compiling langs lexica for $$ll" ; \
		if ! test -e "$$ll.xml " ; then \
			echo " * Backing up to $$ll.xml.$(shell date +%s).bak"  ; \
			cp -R $$ll.xml $$ll.xml.$(shell date +%s).bak ; \
		fi ; \
		$(SAXON) inDir=$(GTHOME)/words/dicts/$$ll/src/ > $$ll.xml ; \
		echo " * Compiling resulted in: " ; \
		wc -l $$ll.xml ; \
	done

.PHONY: print_complete_message
print_complete_message:
print_complete_message:
	@echo 
	@echo 
	@echo "** Built lexica for sanat:            "
	@echo "**    + $(LEX_COMPILE_LANGS)          "
	@echo "**    + $(LEX_COMPILE_WORDS_DICTS)    "
	@echo "** Built FSTs for sanat:              "
	@echo "**    + $(GT_COMPILE_LANGS)           "
	@echo
	@echo

#####
##### #guusaawtargets
#####

GUUSAAW_LANGS_ANALYSERS      :=   hdn
GUUSAAW_LANGS_LEXICA         :=   
GUUSAAW_WORDS_DICTS_LEXICA   :=   hdneng


.PHONY: guusaaw-lexica
guusaaw-lexica: LEX_COMPILE_LANGS := $(GUUSAAW_LANGS_LEXICA)
guusaaw-lexica: LEX_COMPILE_WORDS_DICTS := $(GUUSAAW_WORDS_DICTS_LEXICA)
guusaaw-lexica: compile_langs_lexicon \
			    compile_words_dicts_lexicon

rm-guusaaw-lexica: $(foreach xx, $(GUUSAAW_LANGS_LEXICA), $(xx)-all.xml) \
				   $(foreach yy, $(GUUSAAW_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: guusaaw-install
guusaaw-install: GT_COMPILE_LANGS := $(GUUSAAW_LANGS_ANALYSERS)
guusaaw-install: install_langs_fsts

.PHONY: guusaaw
guusaaw: GT_COMPILE_LANGS := $(GUUSAAW_LANGS_ANALYSERS)
guusaaw: LEX_COMPILE_LANGS := $(GUUSAAW_LANGS_LEXICA)
guusaaw: LEX_COMPILE_WORDS_DICTS := $(GUUSAAW_WORDS_DICTS_LEXICA)
guusaaw: guusaaw-lexica compile_langs_fsts print_complete_message

#####
##### #pikiskwewinatargets
#####

PIKISKWEWINA_LANGS_ANALYSERS      :=   crk
PIKISKWEWINA_LANGS_LEXICA         :=   
PIKISKWEWINA_WORDS_DICTS_LEXICA   :=   crkeng

.PHONY: pikiskwewina-lexica
pikiskwewina-lexica: LEX_COMPILE_LANGS := $(PIKISKWEWINA_LANGS_LEXICA)
pikiskwewina-lexica: LEX_COMPILE_WORDS_DICTS := $(PIKISKWEWINA_WORDS_DICTS_LEXICA)
pikiskwewina-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: pikiskwewina
pikiskwewina: GT_COMPILE_LANGS := $(PIKISKWEWINA_LANGS_ANALYSERS)
pikiskwewina: LEX_COMPILE_LANGS := $(PIKISKWEWINA_LANGS_LEXICA)
pikiskwewina: LEX_COMPILE_WORDS_DICTS := $(PIKISKWEWINA_WORDS_DICTS_LEXICA)
pikiskwewina: pikiskwewina-lexica compile_langs_fsts print_complete_message

rm-pikiskwewina-lexica: $(foreach xx, $(PIKISKWEWINA_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(PIKISKWEWINA_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: pikiskwewina-install
pikiskwewina-install: GT_COMPILE_LANGS := $(PIKISKWEWINA_LANGS_ANALYSERS)
pikiskwewina-install: install_langs_fsts

#####
##### #saantargets
#####

SAAN_LANGS_ANALYSERS      :=   sms fin
SAAN_LANGS_LEXICA         :=   sms
SAAN_WORDS_DICTS_LEXICA   :=   

.PHONY: saan-lexica
saan-lexica: LEX_COMPILE_LANGS := sms
saan-lexica: compile_langs_lexicon

.PHONY: saan-lexica
saan-lexica: LEX_COMPILE_LANGS := $(SAAN_LANGS_LEXICA)
saan-lexica: LEX_COMPILE_WORDS_DICTS := $(SAAN_WORDS_DICTS_LEXICA)
saan-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: saan
saan: GT_COMPILE_LANGS := $(SAAN_LANGS_ANALYSERS)
saan: LEX_COMPILE_LANGS := $(SAAN_LANGS_LEXICA)
saan: LEX_COMPILE_WORDS_DICTS := $(SAAN_WORDS_DICTS_LEXICA)
saan: saan-lexica compile_langs_fsts print_complete_message

rm-saan-lexica: $(foreach xx, $(SAAN_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(SAAN_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: saan-install
saan-install: GT_COMPILE_LANGS := $(SAAN_LANGS_ANALYSERS)
saan-install: install_langs_fsts

#####
##### #vadatargets
#####

VADA_LANGS_ANALYSERS      :=   yrk fin
VADA_LANGS_LEXICA         :=   yrk
VADA_WORDS_DICTS_LEXICA   :=   finyrk

.PHONY: vada-lexica
vada-lexica: LEX_COMPILE_LANGS := $(VADA_LANGS_LEXICA)
vada-lexica: LEX_COMPILE_WORDS_DICTS := $(VADA_WORDS_DICTS_LEXICA)
vada-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: vada
vada: GT_COMPILE_LANGS := $(VADA_LANGS_ANALYSERS)
vada: LEX_COMPILE_LANGS := $(VADA_LANGS_LEXICA)
vada: LEX_COMPILE_WORDS_DICTS := $(VADA_WORDS_DICTS_LEXICA)
vada: vada-lexica compile_langs_fsts print_complete_message

rm-vada-lexica: $(foreach xx, $(VADA_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(VADA_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: vada-install
vada-install: GT_COMPILE_LANGS := $(VADA_LANGS_ANALYSERS)
vada-install: install_langs_fsts

#####
##### #mutertargets
#####

MUTER_LANGS_ANALYSERS      :=   mrj mhr fin rus
MUTER_LANGS_LEXICA         :=   mhr mrj
MUTER_WORDS_DICTS_LEXICA   :=   finmrj

.PHONY: muter-lexica
muter-lexica: LEX_COMPILE_LANGS := $(MUTER_LANGS_LEXICA)
muter-lexica: LEX_COMPILE_WORDS_DICTS := $(MUTER_WORDS_DICTS_LEXICA)
muter-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: muter
muter: GT_COMPILE_LANGS := $(MUTER_LANGS_ANALYSERS)
muter: LEX_COMPILE_LANGS := $(MUTER_LANGS_LEXICA)
muter: LEX_COMPILE_WORDS_DICTS := $(MUTER_WORDS_DICTS_LEXICA)
muter: muter-lexica compile_langs_fsts print_complete_message

rm-muter-lexica: $(foreach xx, $(MUTER_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(MUTER_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: muter-install
muter-install: GT_COMPILE_LANGS := $(MUTER_LANGS_ANALYSERS)
muter-install: install_langs_fsts

#####
##### #valkstargets
#####

VALKS_LANGS_ANALYSERS      :=   fin myv mdf
VALKS_LANGS_LEXICA         :=   myv mdf
VALKS_WORDS_DICTS_LEXICA   :=   finmyv finmdf

.PHONY: valks-lexica
valks-lexica: LEX_COMPILE_LANGS := $(VALKS_LANGS_LEXICA)
valks-lexica: LEX_COMPILE_WORDS_DICTS := $(VALKS_WORDS_DICTS_LEXICA)
valks-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: valks
valks: GT_COMPILE_LANGS := $(VALKS_LANGS_ANALYSERS)
valks: LEX_COMPILE_LANGS := $(VALKS_LANGS_LEXICA)
valks: LEX_COMPILE_WORDS_DICTS := $(VALKS_WORDS_DICTS_LEXICA)
valks: valks-lexica compile_langs_fsts print_complete_message

rm-valks-lexica: $(foreach xx, $(VALKS_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(VALKS_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: valks-install
valks-install: GT_COMPILE_LANGS := $(VALKS_LANGS_ANALYSERS)
valks-install: install_langs_fsts

#####
##### #sanattargets
#####

SANAT_LANGS_ANALYSERS      :=   olo izh liv fin fkv
SANAT_LANGS_LEXICA         :=   olo liv izh
SANAT_WORDS_DICTS_LEXICA   :=   nobfkv finliv fkvnob finolo finizh

# finizh

# NOTE: some temporary fixes to add usage to everything, and include <lg>
# node
# adjust_nobfkv: nobfkv.xml
# 	@echo "*******************************"
# 	@echo "** Adjusting nob-fkv lexicon **"
# 	@echo "*******************************"
# 	@echo "** Backup made (.bak)        **"
# 	@echo "*******************************"
# 	@echo ""
# 	cp $^ $^.tmp
# 	cat $^.tmp | sed 's/<e>/<e usage="vd">/g' | \
# 				 sed 's/  <l /  <lg><l /g'    | \
# 				 sed 's/<\/l>/<\/l><\/lg>/g'  | \
# 				 xmllint --format - \
# 				 > $^
# 	rm $^.tmp

.PHONY: sanat-lexica
sanat-lexica: LEX_COMPILE_LANGS := $(SANAT_LANGS_LEXICA)
sanat-lexica: LEX_COMPILE_WORDS_DICTS := $(SANAT_WORDS_DICTS_LEXICA)
sanat-lexica: compile_langs_lexicon \
			  compile_words_dicts_lexicon

.PHONY: sanat
sanat: GT_COMPILE_LANGS := $(SANAT_LANGS_ANALYSERS)
sanat: LEX_COMPILE_LANGS := $(SANAT_LANGS_LEXICA)
sanat: LEX_COMPILE_WORDS_DICTS := $(SANAT_WORDS_DICTS_LEXICA)
sanat: sanat-lexica compile_langs_fsts print_complete_message

rm-sanat-lexica: $(foreach xx, $(SANAT_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(SANAT_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: sanat-install
sanat-install: GT_COMPILE_LANGS := $(SANAT_LANGS_ANALYSERS)
sanat-install: install_langs_fsts

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

nob-sme.all.xml: $(GTHOME)/words/dicts/nobsme/src/*.xml
	@echo "******************************"
	@echo "** Building nob-sme lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	mkdir nobsme
	cp $^ nobsme/
	$(SAXON) inDir=$(pwd)/nobsme/ > $@
	rm -rf nobsme/

.PHONY: sanit-lexica
sanit-lexica: fin-sme.all.xml \
			  nob-sme.all.xml \
			  sme-fin.all.xml \
			  sme-nob.all.xml

##
### #smeanalysers
##

.PHONY: sanit
sanit: GT_COMPILE_LANGS := sme fin nob
sanit: sanit-lexica compile_langs_fsts
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

.PHONY: sanit-install
sanit-install: GT_COMPILE_LANGS := sme fin nob
sanit-install: install_langs_fsts

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

#####
##### #kyvtargets
#####

KYV_LANGS_ANALYSERS      :=   kpv fin udm
KYV_LANGS_LEXICA         :=   udm
KYV_WORDS_DICTS_LEXICA   :=   kom2X

.PHONY: kyv-lexica
kyv-lexica: LEX_COMPILE_LANGS := $(KYV_LANGS_LEXICA)
kyv-lexica: LEX_COMPILE_WORDS_DICTS := $(KYV_WORDS_DICTS_LEXICA)
kyv-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: kyv
kyv: GT_COMPILE_LANGS := $(KYV_LANGS_ANALYSERS)
kyv: LEX_COMPILE_LANGS := $(KYV_LANGS_LEXICA)
kyv: LEX_COMPILE_WORDS_DICTS := $(KYV_WORDS_DICTS_LEXICA)
kyv: kyv-lexica compile_langs_fsts print_complete_message

rm-kyv-lexica: $(foreach xx, $(KYV_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(KYV_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: kyv-install
kyv-install: GT_COMPILE_LANGS := $(KYV_LANGS_ANALYSERS)
kyv-install: install_langs_fsts copy_molotsov

.PHONY: copy_molotsov
copy_molotsov: $(GTHOME)/langs/kpv/src/analyser-dict-gt-desc-molotsov.xfst
	cp $^ /opt/smi/kpv/bin/analyser-dict-gt-desc-molotsov.xfst


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

.PHONY: all
all: vada  \
	 valks \
	 sanat \
	 saan \
	 sanit \
	 baakoeh \
	 kyv \
	 muter
	@echo $(TARGET_DIR)

.PHONY: all-lexica
all-lexica: baakoeh-lexica \
	guusaaw-lexica \
	kyv-lexica \
	muter-lexica \
	pikiskwewina-lexica \
	saan-lexica \
	sanat-lexica \
	sanit-lexica \
	vada-lexica \
	valks-lexica
	@echo $(TARGET_DIR)

