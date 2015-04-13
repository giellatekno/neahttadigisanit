#######################
##                   ##
## Table of Contents ##
##                   ##
#######################

# TODO: when templates are updated, not everything is noticed in make
# process for main/langs/, so it might be necessary to do a distclean,
# and reautogen from time to time

# *** If you are starting a new project ***
# 	See #sampletargets

# Some helpful tags for jumping around

###         #guusaawtargets
###         
###         #itwewinatargets
###         
###         #dikaneisditargets
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
###         #sonadtargets
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

COLLECT_PARTS_SME_NOB := $(GTHOME)/words/dicts/scripts/collect-dict-parts-nds-smenob.xsl
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
	@echo "** Building $(GT_COMPILE_LANGS) $(GT_COMPILE_STARTUP_LANGS) FSTs **"
	@echo "***********************"
	@echo ""
	for ll in $(GT_COMPILE_LANGS) ; do \
		if ! test -e "$(GTHOME)/langs/$$ll/src/Makefile" ; then \
			cd $(GTHOME)/langs/$$ll ; ./autogen.sh ; ./configure --enable-dicts $(LANGS_FLAGS) ; \
		fi ; \
		cd $(GTHOME)/langs/$$ll ; make ; \
	done 
	for ll in $(GT_COMPILE_STARTUP_LANGS) ; do \
		if ! test -e "$(GTHOME)/startup-langs/$$ll/src/Makefile" ; then \
			cd $(GTHOME)/startup-langs/$$ll ; ./autogen.sh ; ./configure --enable-dicts $(LANGS_FLAGS) ; \
		fi ; \
		cd $(GTHOME)/startup-langs/$$ll ; make ; \
	done 

install_langs_fsts: $(foreach lang, $(GT_COMPILE_LANGS), langs/$(lang)/src/analyser-gt-desc.xfst)
install_langs_fsts: $(langs)
	@echo $*
	@echo "***********************"
	@echo "** Copying to target for: $(GT_COMPILE_LANGS) $(GT_COMPILE_STARTUP_LANGS) **"
	@echo "***********************"
	@echo ""
	for ll in $(GT_COMPILE_LANGS) ; do \
		mkdir -p /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/langs/$$ll/src/analyser-dict-gt-desc.*  /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/langs/$$ll/src/generator-dict-gt-norm.* /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/langs/$$ll/src/generator-dict-gt-desc-mobile.* /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/langs/$$ll/src/analyser-dict-gt-desc-mobile.* /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/langs/$$ll/src/analyser-dict-gt-desc-mobile.*  /opt/smi/$$ll/bin/ ; \
	done 
	for ll in $(GT_COMPILE_STARTUP_LANGS) ; do \
		mkdir -p /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/startup-langs/$$ll/src/analyser-dict-gt-desc.*  /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/startup-langs/$$ll/src/generator-dict-gt-norm.* /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/startup-langs/$$ll/src/generator-dict-gt-desc-mobile.* /opt/smi/$$ll/bin/ ; \
		cp $(GTHOME)/startup-langs/$$ll/src/analyser-dict-gt-desc-mobile.*  /opt/smi/$$ll/bin/ ; \
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
	@echo "** Built lexica for:            "
	@echo "**    + $(LEX_COMPILE_LANGS)          "
	@echo "**    + $(LEX_COMPILE_WORDS_DICTS)    "
	@echo "** Built FSTs for:              "
	@echo "**    + $(GT_COMPILE_LANGS)           "
	@echo
	@echo



###    #####
###    ##### #sampletargets
###    #####
###    
###    ### When starting a new project, copy this whole section (down to
###    ### #/sampletargets), and change the following settings. Then, be sure to
###    ### replace all instances of SAMPLE and sample in variables and target names
###    ### with the PROJNAME.
###    
###    # These are the ISOs of the languages to compile from GTHOME/langs/
###    SAMPLE_LANGS_ANALYSERS           :=   izh liv fin vep vro vot
###
###    # OPTIONAL: enable miscellaneous ./configure flags
###    # SAMPLE_LANGS_FLAGS             :=   --with-hfst
###    
###    # These are the ISOs of the languages to compile from GTHOME/startup-langs/
###    SAMPLE_STARTUP_LANGS_ANALYSERS   :=   lav
###    
###    # Compile the lexicon from within GTHOME/langs/LANG/src/morphology/stems/*.xml
###    
###    SAMPLE_LANGS_LEXICA              :=   liv izh vep vro vot
###    
###    # Compile the lexicon from a directory within GTHOME/words/dicts/
###    SAMPLE_WORDS_DICTS_LEXICA        :=   finliv finizh lavliv
###    
###    .PHONY: sample-lexica
###    sample-lexica: LEX_COMPILE_LANGS := $(SAMPLE_LANGS_LEXICA)
###    sample-lexica: LEX_COMPILE_WORDS_DICTS := $(SAMPLE_WORDS_DICTS_LEXICA)
###    sample-lexica: compile_langs_lexicon \
###    			  compile_words_dicts_lexicon
###    
###    .PHONY: sample
###    sample: GT_COMPILE_LANGS := $(SAMPLE_LANGS_ANALYSERS)
###    sample: GT_COMPILE_STARTUP_LANGS := $(SAMPLE_STARTUP_LANGS_ANALYSERS)
###    sample: LEX_COMPILE_LANGS := $(SAMPLE_LANGS_LEXICA)
###    sample: LEX_COMPILE_WORDS_DICTS := $(SAMPLE_WORDS_DICTS_LEXICA)
###    sample: sample-lexica compile_langs_fsts print_complete_message
###    
###    rm-sample-lexica: $(foreach xx, $(SAMPLE_LANGS_LEXICA), $(xx)-all.xml) \
###    				 $(foreach yy, $(SAMPLE_WORDS_DICTS_LEXICA), $(yy).xml)
###    	@rm -rf $^
###    
###    .PHONY: sample-install
###    sample-install: GT_COMPILE_LANGS := $(SAMPLE_LANGS_ANALYSERS)
###    sample-install: GT_COMPILE_STARTUP_LANGS := $(SAMPLE_STARTUP_LANGS_ANALYSERS)
###    sample-install: install_langs_fsts
###    
###    #####
###    ##### #/sampletargets
###    #####


#####
##### #ndstestingtargets
#####

# These are the ISOs of the languages to compile from GTHOME/langs/
NDSTESTING_LANGS_ANALYSERS           :=   kca nob rus

# These are the ISOs of the languages to compile from GTHOME/startup-langs/
NDSTESTING_STARTUP_LANGS_ANALYSERS   :=   

# Compile the lexicon from within GTHOME/langs/LANG/src/morphology/stems/*.xml

NDSTESTING_LANGS_LEXICA              :=   kca

# Compile the lexicon from a directory within GTHOME/words/dicts/
NDSTESTING_WORDS_DICTS_LEXICA        :=   

.PHONY: ndstesting-lexica
ndstesting-lexica: LEX_COMPILE_LANGS := $(NDSTESTING_LANGS_LEXICA)
ndstesting-lexica: LEX_COMPILE_WORDS_DICTS := $(NDSTESTING_WORDS_DICTS_LEXICA)
ndstesting-lexica: compile_langs_lexicon \
			  compile_words_dicts_lexicon

.PHONY: ndstesting
ndstesting: GT_COMPILE_LANGS := $(NDSTESTING_LANGS_ANALYSERS)
ndstesting: GT_COMPILE_STARTUP_LANGS := $(NDSTESTING_STARTUP_LANGS_ANALYSERS)
ndstesting: LEX_COMPILE_LANGS := $(NDSTESTING_LANGS_LEXICA)
ndstesting: LEX_COMPILE_WORDS_DICTS := $(NDSTESTING_WORDS_DICTS_LEXICA)
ndstesting: ndstesting-lexica compile_langs_fsts print_complete_message

rm-ndstesting-lexica: $(foreach xx, $(NDSTESTING_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(NDSTESTING_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: ndstesting-install
ndstesting-install: GT_COMPILE_LANGS := $(NDSTESTING_LANGS_ANALYSERS)
ndstesting-install: GT_COMPILE_STARTUP_LANGS := $(NDSTESTING_STARTUP_LANGS_ANALYSERS)
ndstesting-install: install_langs_fsts

#####
##### #/ndstestingtargets
#####


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
##### #dikaneisditargets
#####

DIKANEISDI_LANGS_ANALYSERS      :=   chr
DIKANEISDI_LANGS_LEXICA         :=
DIKANEISDI_WORDS_DICTS_LEXICA   :=   chreng

.PHONY: dikaneisdi-lexica
dikaneisdi-lexica: LEX_COMPILE_LANGS := $(DIKANEISDI_LANGS_LEXICA)
dikaneisdi-lexica: LEX_COMPILE_WORDS_DICTS := $(DIKANEISDI_WORDS_DICTS_LEXICA)
dikaneisdi-lexica: compile_langs_lexicon \
			        compile_words_dicts_lexicon

.PHONY: dikaneisdi-lexica
dikaneisdi-lexica: LEX_COMPILE_LANGS := $(DIKANEISDI_LANGS_LEXICA)
dikaneisdi-lexica: LEX_COMPILE_WORDS_DICTS := $(DIKANEISDI_WORDS_DICTS_LEXICA)
dikaneisdi-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: dikaneisdi
dikaneisdi: GT_COMPILE_LANGS := $(DIKANEISDI_LANGS_ANALYSERS)
dikaneisdi: LEX_COMPILE_LANGS := $(DIKANEISDI_LANGS_LEXICA)
dikaneisdi: LEX_COMPILE_WORDS_DICTS := $(DIKANEISDI_WORDS_DICTS_LEXICA)
dikaneisdi: dikaneisdi-lexica compile_langs_fsts print_complete_message

rm-dikaneisdi-lexica: $(foreach xx, $(DIKANEISDI_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(DIKANEISDI_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: dikaneisdi-install
dikaneisdi-install: GT_COMPILE_LANGS := $(DIKANEISDI_LANGS_ANALYSERS)
dikaneisdi-install: install_langs_fsts


#####
##### #itwewinatargets
#####

ITWEWINA_LANGS_ANALYSERS      :=   crk
ITWEWINA_LANGS_FLAGS          :=   --with-hfst
ITWEWINA_LANGS_LEXICA         :=   
# Generalized target, but we have some exceptions here, so crkeng is commented
# out.
# crkeng
ITWEWINA_WORDS_DICTS_LEXICA   :=   

# NB: if things are in priv, use $(GTPRIV)
#


CRKENG_DIRS  := $(GTHOME)/art/dicts/crk/Wolvengrey/ \
				$(GTHOME)/art/dicts/crk/Maskwacis/


# add more directories as a list to CRKENG_DIRS
#
#  CRKENG_DIRS  := /path/to/dir/ /path/to/dir2/ /path/to/dir3/

# TODO: for now /scripts/ is copied to make sure that things work, and deleted at
# the end. in the future, remove this.
crkeng.xml: $(foreach d, $(CRKENG_DIRS), $(shell find $d -name '*.xml'))
	@echo "******************************"
	@echo "** Building crk-eng lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	mkdir -p crkeng_tmp/
	cp -R $(GTHOME)/words/dicts/scripts ../scripts
	cp $^ crkeng_tmp/
	$(SAXON) inDir=$(pwd)/crkeng_tmp/ > $@
	@rm -rf crkeng_tmp/
	@rm -rf ../scripts

.PHONY: itwewina-lexica
itwewina-lexica: LEX_COMPILE_LANGS := $(ITWEWINA_LANGS_LEXICA)
itwewina-lexica: LEX_COMPILE_WORDS_DICTS := $(ITWEWINA_WORDS_DICTS_LEXICA)
itwewina-lexica: crkeng.xml compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: itwewina
itwewina: GT_COMPILE_LANGS := $(ITWEWINA_LANGS_ANALYSERS)
itwewina: LEX_COMPILE_LANGS := $(ITWEWINA_LANGS_LEXICA)
itwewina: LEX_COMPILE_WORDS_DICTS := $(ITWEWINA_WORDS_DICTS_LEXICA)
itwewina: LANGS_FLAGS := $(ITWEWINA_LANGS_FLAGS)
itwewina: itwewina-lexica compile_langs_fsts print_complete_message

rm-itwewina-lexica: $(foreach xx, $(ITWEWINA_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(ITWEWINA_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: copy-itwewina-variants
copy-itwewina-variants: $(GTHOME)/langs/crk/src/analyser-dict-gt-desc-mobile.* \
						$(GTHOME)/langs/crk/src/analyser-dict-gt-desc.* \
						$(GTHOME)/langs/crk/src/generator-dict-gt-norm.*
	@-cp $^ /opt/smi/crk/bin/


.PHONY: itwewina-install 
itwewina-install: GT_COMPILE_LANGS := $(ITWEWINA_LANGS_ANALYSERS)
itwewina-install: install_langs_fsts copy-itwewina-variants

# copy-itwewina-variants


#####
##### #saantargets
#####

SAAN_LANGS_ANALYSERS      :=   sms fin
SAAN_LANGS_FLAGS          :=   --with-hfst --enable-twostep-intersect --no-recursion
SAAN_LANGS_LEXICA         :=   sms
SAAN_WORDS_DICTS_LEXICA   :=   sms2X

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
saan: LANGS_FLAGS := $(SAAN_LANGS_FLAGS)
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

SANAT_LANGS_ANALYSERS      :=   olo fin fkv
SANAT_LANGS_LEXICA         :=   olo izh
SANAT_WORDS_DICTS_LEXICA   :=   nobfkv fkvnob finolo

# finizh

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
##### #sonadtargets
#####

SONAD_LANGS_ANALYSERS           :=   izh liv fin vep vro vot
SONAD_STARTUP_LANGS_ANALYSERS   :=   lav
SONAD_LANGS_LEXICA              :=   liv izh vep vro vot
SONAD_WORDS_DICTS_LEXICA        :=   finliv finizh lavliv

.PHONY: sonad-lexica
sonad-lexica: LEX_COMPILE_LANGS := $(SONAD_LANGS_LEXICA)
sonad-lexica: LEX_COMPILE_WORDS_DICTS := $(SONAD_WORDS_DICTS_LEXICA)
sonad-lexica: compile_langs_lexicon \
			  compile_words_dicts_lexicon

.PHONY: sonad
sonad: GT_COMPILE_LANGS := $(SONAD_LANGS_ANALYSERS)
sonad: GT_COMPILE_STARTUP_LANGS := $(SONAD_STARTUP_LANGS_ANALYSERS)
sonad: LEX_COMPILE_LANGS := $(SONAD_LANGS_LEXICA)
sonad: LEX_COMPILE_WORDS_DICTS := $(SONAD_WORDS_DICTS_LEXICA)
sonad: sonad-lexica compile_langs_fsts print_complete_message

rm-sonad-lexica: $(foreach xx, $(SONAD_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(SONAD_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: sonad-install
sonad-install: GT_COMPILE_LANGS := $(SONAD_LANGS_ANALYSERS)
sonad-install: GT_COMPILE_STARTUP_LANGS := $(SONAD_STARTUP_LANGS_ANALYSERS)
sonad-install: install_langs_fsts

#####
##### #sanittargets
#####

##
### #sanitlexica
##

# NB: these are different than the langs/ lexica
# also, need to filter here
# TODO: filter out entries without usage="nds" 
sme-nob.all.xml: $(GTHOME)/words/dicts/smenob/src/
	@echo "******************************"
	@echo "** Building sme-nob lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON_SME_NOB) inDir=$^ > $@

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
	mkdir -p nobsme
	-@cp -r $(GTHOME)/words/dicts/nobsme/dtd dtd
	cp $^ nobsme/
	$(SAXON) inDir=$(pwd)/nobsme/ > $@
	rm -rf nobsme/
	rm -rf dtd/

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
KYV_LANGS_LEXICA         :=   udm kpv
KYV_WORDS_DICTS_LEXICA   :=   finkpv

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

BACKS := $(shell ls -c1 *.xml.*.bak | sed "s/\.xml.[0-9]*\.bak//" | sort | uniq)


 # | sed 's/\./   /g' | cut -f 1 | sort -u > dicts.tmp

# This will store all old dictionaries with a particular suffix and
# *.xml.bak in an archive. Each archive will be expanded and
# recompressed if new files are found. We need backups, but they take up
# a lot of space in some cases 
#
.PHONY: collect-backups
collect-backups:
	@echo $(BACKS)
	@echo "******************************"
	@echo "** (re-)compressing backups **"
	@echo "******************************"
	@echo ""
	for b in $(BACKS) ; do \
		echo "** Recompressing: $$b" ; \
		tar -jxvf $$b.backups.tar.bz2 ; \
		rm $$b.backups.tar.bz2 ; \
		echo "** Adding: " ; \
		ls -c1 $$b.xml.*.bak ; \
		BZIP=--best tar -jcf $$b.backups.tar.bz2 $$b.xml.*.bak ; \
		rm $$b.xml.*.bak ; \
	done 

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
	itwewina-lexica \
	saan-lexica \
	sanat-lexica \
	sonad-lexica \
	sanit-lexica \
	vada-lexica \
	valks-lexica
	@echo $(TARGET_DIR)

