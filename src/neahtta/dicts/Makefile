#######################
##                   ##
## Table of Contents ##
##                   ##
#######################

# include for sme-sma


# TODO: when templates are updated, not everything is noticed in make
# process for giellalt/lang-xxx/, so it might be necessary to do a distclean,
# and reautogen from time to time

# *** If you are starting a new project ***
# 	See #sampletargets

# Some helpful tags for jumping around

VIRTUALENV := $

###         #guusaawtargets
###
###         #itwewinatargets
###
###         #gunahatargets
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
###         #focailtargets
###
###         #cuvantultargets
###
###         #Globaltargets

# Use GSED if available. Probably a good idea for macs.
#
#SED := $(shell which gsed sed | head -n 1)
SED := $(shell which sed | head -n 1)

# VERBOSE ?=
BUILD_FLAGS := -v

# ifeq ($(VERBOSE),true)
# 	BUILD_FLAGS := -v
# else
# 	BUILD_FLAGS :=
# endif

#SAXON_JAR = $(shell which saxon9.jar)
SAXON_JAR = $(HOME)/bin/saxon9.jar

COLLECT_PARTS := $(GTHOME)/words/dicts/scripts/collect-dict-parts.xsl
SAXON := java -Xmx2048m -cp $(SAXON_JAR) \
		 -Dfile.encoding=UTF8 net.sf.saxon.Transform \
		 -it:main $(COLLECT_PARTS)

COLLECT_PARTS_SME_NOB := $(GTHOME)/words/dicts/scripts/collect-dict-parts-nds-smenob.xsl
SAXON_SME_NOB := java -Xmx2048m -cp $(SAXON_JAR) \
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
# this only works with new-infra language (~/gtsvn/giellalt/lang-xxx/), so languages
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

# define space so that it can actually replace
space :=
space +=

comma :=,

compile_langs_fsts: $(foreach lang, $(GT_COMPILE_LANGS), giellalt/lang-$(lang)/src/analyser-gt-desc.xfst)
compile_langs_fsts: $(langs)
	@echo $*
	@echo "***********************"
	@echo "** Building $(GT_COMPILE_LANGS) FSTs **"
	@echo "***********************"
	@echo ""
	./build_langs.sh $(BUILD_FLAGS) -l $(subst $(space),$(comma),$(GT_COMPILE_LANGS)) -- --enable-dicts $(LANGS_FLAGS)

install_langs_fsts: $(foreach lang, $(GT_COMPILE_LANGS), giellalt/lang-$(lang)/src/analyser-gt-desc.xfst)
install_langs_fsts: $(langs)
	@echo $*
	@echo "***********************"
	@echo "** Copying to target for: $(GT_COMPILE_LANGS) **"
	@echo "***********************"
	@echo ""
	for ll in $(GT_COMPILE_LANGS) ; do \
		mkdir -p /opt/smi/$$ll/bin/ ; \
		cp $(GTLANGS)/lang-$$ll/src/analyser-dict-gt-desc.*  /opt/smi/$$ll/bin/ ; \
		cp $(GTLANGS)/lang-$$ll/src/generator-dict-gt-norm.* /opt/smi/$$ll/bin/ ; \
		cp $(GTLANGS)/lang-$$ll/src/analyser-dict-gt-desc-mobile.*  /opt/smi/$$ll/bin/ ; \
	done

.PHONY: clean_langs_fsts
clean_langs_fsts: $(foreach lang, $(GT_COMPILE_LANGS), giellalt/lang-$(lang)/src/analyser-gt-desc.xfst)
clean_langs_fsts: $(langs)
	@echo $*
	@echo "***********************"
	@echo "** Cleaning $(GT_COMPILE_LANGS) FSTs **"
	@echo "***********************"
	@echo ""
	for ll in $(GT_COMPILE_LANGS) ; do \
		echo "Make clean in $(GTLANGS)/lang-$$ll" ; \
		cd $(GTLANGS)/lang-$$ll ; make clean ; cd .. \
	done
	cd $(GTLANGS)/giella-core/ ; git pull ; make

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
		$(SAXON) inDir=$(GTLANGS)/lang-$$ll/src/fst/stems/ > $$ll-all.xml ; \
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
###    # These are the ISOs of the languages to compile from GTLANGS/lang-xxx/
###    SAMPLE_LANGS_ANALYSERS           :=   izh liv fin vep vro vot
###
###    # OPTIONAL: enable miscellaneous ./configure flags
###    # SAMPLE_LANGS_FLAGS             :=   --with-hfst
###
###    # Compile the lexicon from within GTLANGS/lang-xxx/src/fst/stems/*.xml
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
###    sample: LEX_COMPILE_LANGS := $(SAMPLE_LANGS_LEXICA)
###    sample: LEX_COMPILE_WORDS_DICTS := $(SAMPLE_WORDS_DICTS_LEXICA)
###    sample: sample-lexica compile_langs_fsts print_complete_message
###
###    .PHONY: sample-clean
###    sample-clean:  GT_COMPILE_LANGS :=  $(SAMPLE_LANGS_ANALYSERS)
###    sample-clean: clean_langs_fsts
###
###    rm-sample-lexica: $(foreach xx, $(SAMPLE_LANGS_LEXICA), $(xx)-all.xml) \
###    				 $(foreach yy, $(SAMPLE_WORDS_DICTS_LEXICA), $(yy).xml)
###    	@rm -rf $^
###
###    .PHONY: sample-install
###    sample-install: GT_COMPILE_LANGS := $(SAMPLE_LANGS_ANALYSERS)
###    sample-install: install_langs_fsts
###
###    #####
###    ##### #/sampletargets
###    #####


#####
##### #ndstestingtargets
#####

# These are the ISOs of the languages to compile from GTLANGS/lang-xxx/
NDSTESTING_LANGS_ANALYSERS           :=   kca nob rus

# Compile the lexicon from within GTLANGS/lang-xxx/src/fst/stems/*.xml

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
ndstesting: LEX_COMPILE_LANGS := $(NDSTESTING_LANGS_LEXICA)
ndstesting: LEX_COMPILE_WORDS_DICTS := $(NDSTESTING_WORDS_DICTS_LEXICA)
ndstesting: ndstesting-lexica compile_langs_fsts print_complete_message

rm-ndstesting-lexica: $(foreach xx, $(NDSTESTING_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(NDSTESTING_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: ndstesting-install
ndstesting-install: GT_COMPILE_LANGS := $(NDSTESTING_LANGS_ANALYSERS)
ndstesting-install: install_langs_fsts

.PHONY: ndstesting-clean
ndstesting-clean:  GT_COMPILE_LANGS :=  $(NDSTESTING_LANGS_ANALYSERS)
ndstesting-clean: clean_langs_fsts


#####
##### #/ndstestingtargets
#####

#####
##### #cuvantultargets
#####

CUVANTUL_LANGS_ANALYSERS      :=   ron
CUVANTUL_LANGS_LEXICA         :=
CUVANTUL_WORDS_DICTS_LEXICA   :=   ronnob nobron

# .PHONY: cuvantul-lexica
# cuvantul-lexica: LEX_COMPILE_LANGS := $(CUVANTUL_LANGS_LEXICA)
# cuvantul-lexica: LEX_COMPILE_WORDS_DICTS := $(CUVANTUL_WORDS_DICTS_LEXICA)
# cuvantul-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: cuvantul-lexica
cuvantul-lexica: LEX_COMPILE_LANGS := $(CUVANTUL_LANGS_LEXICA)
cuvantul-lexica: LEX_COMPILE_WORDS_DICTS := $(CUVANTUL_WORDS_DICTS_LEXICA)
cuvantul-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: cuvantul
cuvantul: GT_COMPILE_LANGS := $(CUVANTUL_LANGS_ANALYSERS)
cuvantul: LEX_COMPILE_LANGS := $(CUVANTUL_LANGS_LEXICA)
cuvantul: LEX_COMPILE_WORDS_DICTS := $(CUVANTUL_WORDS_DICTS_LEXICA)
cuvantul: cuvantul-lexica compile_langs_fsts print_complete_message

rm-cuvantul-lexica: $(foreach xx, $(CUVANTUL_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(CUVANTUL_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: cuvantul-install
cuvantul-install: GT_COMPILE_LANGS := $(CUVANTUL_LANGS_ANALYSERS)
#cuvantul-install: install_langs_fsts


#####
##### #/cuvantultargets
#####


#####
##### #saanihtargets
#####

### When starting a new project, copy this whole section (down to
### #/saanihtargets), and change the following settings. Then, be sure to
### replace all instances of SAANIH and saanih in variables and target names
### with the PROJNAME.

# These are the ISOs of the languages to compile from GTLANGS/lang-xxx/
SAANIH_LANGS_ANALYSERS           :=   smn fin sme

# OPTIONAL: enable miscellaneous ./configure flags
# SAANIH_LANGS_FLAGS             :=   --with-hfst

# Compile the lexicon from within GTLANGS/lang-xxx/src/fst/stems/*.xml

# SAANIH_LANGS_LEXICA              :=   smn

# Compile the lexicon from a directory within GTHOME/words/dicts/
SAANIH_WORDS_DICTS_LEXICA        :=   smnfin finsmn smnsme smesmn
# finsmn

.PHONY: saanih-lexica
saanih-lexica: LEX_COMPILE_LANGS := $(SAANIH_LANGS_LEXICA)
saanih-lexica: LEX_COMPILE_WORDS_DICTS := $(SAANIH_WORDS_DICTS_LEXICA)
saanih-lexica: compile_langs_lexicon \
			  compile_words_dicts_lexicon

.PHONY: saanih
saanih: GT_COMPILE_LANGS := $(SAANIH_LANGS_ANALYSERS)
saanih: LEX_COMPILE_LANGS := $(SAANIH_LANGS_LEXICA)
saanih: LEX_COMPILE_WORDS_DICTS := $(SAANIH_WORDS_DICTS_LEXICA)
saanih: saanih-lexica compile_langs_fsts print_complete_message

rm-saanih-lexica: $(foreach xx, $(SAANIH_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(SAANIH_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: saanih-install
saanih-install: GT_COMPILE_LANGS := $(SAANIH_LANGS_ANALYSERS)
saanih-install: install_langs_fsts

#####
##### #/saanihtargets
#####

#####
##### #sanjtargets
#####

# These are the ISOs of the languages to compile from GTLANGS/lang-xxx/
SANJ_LANGS_ANALYSERS           :=   sjd-x-private

# OPTIONAL: enable miscellaneous ./configure flags
# SANJ_LANGS_FLAGS             :=   --with-hfst

# Compile the lexicon from within GTLANGS/lang-xxx/src/fst/stems/*.xml

# SANJ_LANGS_LEXICA              :=   smn

# Compile the lexicon from a directory within GTHOME/words/dicts/
# SANJ_WORDS_DICTS_LEXICA        :=   smnfin finsmn smnsme smesmn
# finsmn

.PHONY: sanj-lexica
#sanj-lexica: LEX_COMPILE_LANGS := $(SANJ_LANGS_LEXICA)
#sanj-lexica: LEX_COMPILE_WORDS_DICTS := $(SANJ_WORDS_DICTS_LEXICA)
#sanj-lexica: compile_langs_lexicon \
			  compile_words_dicts_lexicon

# Custom compile script because the xml files are in lang-sjd-x-private/misc, which is not the case in any other dicts.
# Remember to extract xml files from source xlsx files using the scripts in lang-sjd-x-private/src/scripts
SJDRUS_LEXICON_INDIR = $(GTLANGS)/lang-sjd-x-private/misc/xml_sjdrus
RUSSJD_LEXICON_INDIR = $(GTLANGS)/lang-sjd-x-private/misc/xml_russjd
sanj-lexica: 
	@echo $*
	@echo "***********************"
	@echo "** Copying to target for: sjdrus russjd **"
	@echo "***********************"
	@echo ""
	echo " * Compiling langs lexica for sjdrus" ; \
	if ! test -e "sjd-rus.xml " ; then \
		echo " * Backing up to sjd-rus.xml.$(shell date +%s).bak"  ; \
		cp -R sjd-rus.xml sjd-rus.xml.$(shell date +%s).bak ; \
	fi ; \
	if test -d "$(SJDRUS_LEXICON_INDIR)"  ; then \
		$(SAXON) inDir=$(SJDRUS_LEXICON_INDIR) > sjd-rus.xml ; \
		echo " * Compiling resulted in: " ; \
		wc -l sjd-rus.xml ;\
	else \
		echo "Error: The directory $(SJDRUS_LEXICON_INDIR) does not exist. Cannot compile dictionary." ;\
	fi ; \
	echo " * Compiling langs lexica for russjd" ; \
	if ! test -e "rus-sjd.xml " ; then \
		echo " * Backing up to rus-sjd.xml.$(shell date +%s).bak"  ; \
		cp -R sjd-rus.xml rus-sjd.xml.$(shell date +%s).bak ; \
	fi ; \
	if test -d "$(RUSSJD_LEXICON_INDIR)" ; then \
		$(SAXON) inDir=$(RUSSJD_LEXICON_INDIR) > rus-sjd.xml ; \
		echo " * Compiling resulted in: " ; \
		wc -l rus-sjd.xml ;\
	else \
		echo "Error: The directory $(RUSSJD_LEXICON_INDIR) does not exist. Cannot compile dictionary." ;\
	fi ; \

.PHONY: sanj
sanj: GT_COMPILE_LANGS := $(SANJ_LANGS_ANALYSERS)
sanj: LEX_COMPILE_LANGS := $(SANJ_LANGS_LEXICA)
sanj: LEX_COMPILE_WORDS_DICTS := $(SANJ_WORDS_DICTS_LEXICA)
sanj: sanj-lexica compile_langs_fsts print_complete_message

rm-sanj-lexica: 
	@rm -f sjd-rus.xml rus-sjd.xml

.PHONY: sanj-install
sanj-install: GT_COMPILE_LANGS := $(SANJ_LANGS_ANALYSERS)
sanj-install: install_langs_fsts

#####
##### #/sanjtargets
#####


#####
##### #guusaawtargets
#####

GUUSAAW_LANGS_ANALYSERS      :=   hdn
GUUSAAW_LANGS_LEXICA         :=
GUUSAAW_LANGS_FLAGS          :=   --with-hfst
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

.PHONY: guusaaw-clean
guusaaw-clean:  GT_COMPILE_LANGS :=  $(GUUSAAW_LANGS_ANALYSERS)
guusaaw-clean: clean_langs_fsts

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

.PHONY: dikaneisdi-clean
dikaneisdi-clean:  GT_COMPILE_LANGS :=  $(DIKANEISDI_LANGS_ANALYSERS)
dikaneisdi-clean: clean_langs_fsts

rm-dikaneisdi-lexica: $(foreach xx, $(DIKANEISDI_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(DIKANEISDI_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: dikaneisdi-install
dikaneisdi-install: GT_COMPILE_LANGS := $(DIKANEISDI_LANGS_ANALYSERS)
dikaneisdi-install: install_langs_fsts

#####
##### #kidwinantargets
#####

KIDWINAN_LANGS_ANALYSERS      :=   otw
KIDWINAN_LANGS_FLAGS          :=   --with-hfst --without-xfst --without-foma --enable-glossers
KIDWINAN_LANGS_LEXICA         :=
# Generalized target, but we have some exceptions here, so otweng is commented
# out.
# otweng
KIDWINAN_WORDS_DICTS_LEXICA   :=

.PHONY: kidwinan-lexica
kidwinan-lexica: LEX_COMPILE_LANGS := $(KIDWINAN_LANGS_LEXICA)
kidwinan-lexica: LEX_COMPILE_WORDS_DICTS := $(KIDWINAN_WORDS_DICTS_LEXICA)
kidwinan-lexica: otweng.xml compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: kidwinan
kidwinan: GT_COMPILE_LANGS := $(KIDWINAN_LANGS_ANALYSERS)
kidwinan: LEX_COMPILE_LANGS := $(KIDWINAN_LANGS_LEXICA)
kidwinan: LEX_COMPILE_WORDS_DICTS := $(KIDWINAN_WORDS_DICTS_LEXICA)
kidwinan: LANGS_FLAGS := $(KIDWINAN_LANGS_FLAGS)
kidwinan: kidwinan-lexica compile_langs_fsts print_complete_message

.PHONY: kidwinan-clean
kidwinan-clean:  GT_COMPILE_LANGS :=  $(KIDWINAN_LANGS_ANALYSERS)
kidwinan-clean: clean_langs_fsts

rm-kidwinan-lexica: $(foreach xx, $(KIDWINAN_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(KIDWINAN_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: kidwinan-install
kidwinan-install: GT_COMPILE_LANGS := $(KIDWINAN_LANGS_ANALYSERS)
kidwinan-install: install_langs_fsts copy-kidwinan-glossers

# include foma
.PHONY: copy-kidwinan-glossers
copy-kidwinan-glossers: $(GTLANGS)/lang-otw/src/analyser-gt-glossing.* $(GTLANGS)/lang-otw/src/generator-gt-glossing.*
	@-cp $^ /opt/smi/otw/bin/

otweng.xml: $(GTHOME)/art/dicts/otw/otweng.xml
	@echo "******************************"
	@echo "** Building crk-eng lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	mkdir -p otweng_tmp/
	cp $^ otweng_tmp/
	cp -R $(GTHOME)/words/dicts/scripts ../scripts
	$(SAXON) inDir=$(shell pwd)/otweng_tmp > $@
	rm -rf otweng_tmp/

#####
##### #gunahatargets
#####

GUNAHA_LANGS_ANALYSERS      := srs
GUNAHA_LANGS_FLAGS          :=   --without-hfst --without-xfst --with-foma
GUNAHA_LANGS_LEXICA         :=
# Generalized target, but we have some exceptions here, so srseng is commented
# out.
# srseng
GUNAHA_WORDS_DICTS_LEXICA   :=   srseng

.PHONY: gunaha-lexica
gunaha-lexica: LEX_COMPILE_LANGS := $(GUNAHA_LANGS_LEXICA)
gunaha-lexica: LEX_COMPILE_WORDS_DICTS := $(GUNAHA_WORDS_DICTS_LEXICA)
gunaha-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: gunaha
gunaha: GT_COMPILE_LANGS := $(GUNAHA_LANGS_ANALYSERS)
gunaha: LEX_COMPILE_LANGS := $(GUNAHA_LANGS_LEXICA)
gunaha: LEX_COMPILE_WORDS_DICTS := $(GUNAHA_WORDS_DICTS_LEXICA)
gunaha: LANGS_FLAGS := $(GUNAHA_LANGS_FLAGS)
gunaha: gunaha-lexica compile_langs_fsts print_complete_message

.PHONY: gunaha-clean
gunaha-clean:  GT_COMPILE_LANGS :=  $(GUNAHA_LANGS_ANALYSERS)
gunaha-clean: clean_langs_fsts

rm-gunaha-lexica: $(foreach xx, $(GUNAHA_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(GUNAHA_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: gunaha-install
gunaha-install: GT_COMPILE_LANGS := $(GUNAHA_LANGS_ANALYSERS)
gunaha-install: install_langs_fsts copy-gunaha-variants

# include foma
.PHONY: copy-gunaha-variants
copy-gunaha-variants: $(GTLANGS)/lang-srs/src/*.foma
	@-cp $^ /opt/smi/srs/bin/

#####
##### #itwewinatargets
#####

ITWEWINA_LANGS_ANALYSERS      :=   crk
ITWEWINA_LANGS_FLAGS          :=   --with-hfst --disable-syntax --without-xfst
ITWEWINA_LANGS_LEXICA         :=
# Generalized target, but we have some exceptions here, so crkeng is commented
# out.
# crkeng
ITWEWINA_WORDS_DICTS_LEXICA   :=

# NB: if things are in priv, use $(GTPRIV)
#


CRKENG_DIRS  := $(GTHOME)/art/dicts/crk/Wolvengrey/ \
				$(GTHOME)/art/dicts/crk/Maskwacis/

engcrk.xml: $(GTHOME)/art/dicts/crk/Wolvengrey/engcrk.xml
	@echo "******************************"
	@echo "** Building crk-eng lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	mkdir -p crkeng_tmp/
	cat $^ | $(SED) -e 's/pos="\(\w*\)"/pos="\L\1"/' | $(SED) -e 's/pos="\(.\)/pos="\U\1/' > $@

# add more directories as a list to CRKENG_DIRS
#
#  CRKENG_DIRS  := /path/to/dir/ /path/to/dir2/ /path/to/dir3/

# TODO: for now /scripts/ is copied to make sure that things work, and deleted at
# the end. in the future, remove this.

# TODO: include python tools/extract_audio.py --local-audio-source --output-file=OUTFILE dicts/src/INFILE static/aud/crk

# Copy the dependencies and combine them using SAXON
# NB: audio installation process, the URLs in the xml file will be
# rewritten to be something like:
#     aud/crk/etc.mp3
#
# With the intent that 'static' can be dynamically added in jinja
# templates with:
#     url_for('static', filename='aud/crk/etc.mp3')
#
# This seems to be the easiest way to manage the subdirectory path
# 'itwewina/' in the URL, or any potential path
crkeng.xml: $(GTHOME)/art/dicts/crk/Wolvengrey/crkeng.xml \
			$(GTHOME)/art/dicts/crk/Wolvengrey/bridge2FST.xml
	@echo "******************************"
	@echo "** Building crk-eng lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	mkdir -p crkeng_tmp/
	cp $^ crkeng_tmp/
	cp -R $(GTHOME)/words/dicts/scripts ../scripts
	$(SAXON) inDir=$(shell pwd)/crkeng_tmp > $@.tmp
	mkdir -p ../static/aud/crk
	python ../tools/extract_audio.py --local-audio-source --encoding-format=mp3 --output-file=$@.tmp.2 $@.tmp ../static/aud/crk
	cat $@.tmp.2 | sed 's#/../static/##g' > $@
	rm $@.tmp $@.tmp.2
	rm -rf crkeng_tmp/

crkeng-cans.xml: crkeng.xml
	@echo "****************************************"
	@echo "** Building crk-eng-syllabics lexicon **"
	@echo "****************************************"
	@echo "  1.) filter lg/l"
	cat $^ | python ../tools/filter_xpath.py "./e" "./lg/l" "hfst_lookup" $(GTLANGS)/lang-crk/src/orthography/Latn-to-Cans.lookup.hfst > $@.tmp
	@echo "  2.) filter lg/stem"
	cat $@.tmp | python ../tools/filter_xpath.py "./e" "./lg/stem" "hfst_lookup" $(GTLANGS)/lang-crk/src/orthography/Latn-to-Cans.lookup.hfst > $@
	rm $@.tmp


crkeng-macron.xml: crkeng.xml
	@echo "*************************************"
	@echo "** Building crk-eng-macron lexicon **"
	@echo "*************************************"
	@echo "** Backup made (.bak)       **"
	@echo "*************************************"
	@echo ""
	@echo $(SED)
	cat crkeng.xml | $(SED) -e 's/pos="\(.\)/pos="\U\1/'  \
					| $(SED) -e 's/â/ā/'  \
					| $(SED) -e 's/ê/ē/'  \
					| $(SED) -e 's/î/ī/'  \
					| $(SED) -e 's/ô/ō/'  \
					> $@

engcrk-macron.xml: engcrk.xml
	@echo "*************************************"
	@echo "** Building eng-crk-macron lexicon **"
	@echo "*************************************"
	@echo "** Backup made (.bak)       **"
	@echo "*************************************"
	@echo ""
	@echo $(SED)
	cat engcrk.xml | $(SED) -e 's/pos="\(.\)/pos="\U\1/'  \
					| $(SED) -e 's/â/ā/'  \
					| $(SED) -e 's/ê/ē/'  \
					| $(SED) -e 's/î/ī/'  \
					| $(SED) -e 's/ô/ō/'  \
					> $@

engcrk-cans.xml: engcrk.xml
	@echo "****************************************"
	@echo "** Building crk-eng-syllabics lexicon **"
	@echo "****************************************"
	@echo "  1.) filter mg/tg/t"
	cat $^ | python ../tools/filter_xpath.py "./e" "./mg/tg/t" "hfst_lookup" $(GTLANGS)/lang-crk/src/orthography/Latn-to-Cans.lookup.hfst > $@




.PHONY: itwewina-lexica
itwewina-lexica: LEX_COMPILE_LANGS := $(ITWEWINA_LANGS_LEXICA)
itwewina-lexica: LEX_COMPILE_WORDS_DICTS := $(ITWEWINA_WORDS_DICTS_LEXICA)
itwewina-lexica: crkeng.xml engcrk.xml engcrk-macron.xml engcrk-cans.xml crkeng-macron.xml crkeng-cans.xml compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: itwewina
itwewina: GT_COMPILE_LANGS := $(ITWEWINA_LANGS_ANALYSERS)
itwewina: LEX_COMPILE_LANGS := $(ITWEWINA_LANGS_LEXICA)
itwewina: LEX_COMPILE_WORDS_DICTS := $(ITWEWINA_WORDS_DICTS_LEXICA)
itwewina: LANGS_FLAGS := $(ITWEWINA_LANGS_FLAGS)
itwewina: itwewina-lexica compile_langs_fsts print_complete_message

.PHONY: itwewina-clean
itwewina-clean:  GT_COMPILE_LANGS :=  $(ITWEWINA_LANGS_ANALYSERS)
itwewina-clean: clean_langs_fsts

rm-itwewina-lexica: $(foreach xx, $(ITWEWINA_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(ITWEWINA_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: copy-itwewina-variants
copy-itwewina-variants: $(GTLANGS)/lang-crk/src/analyser-dict-gt-desc-mobile.* \
						$(GTLANGS)/lang-crk/src/analyser-dict-gt-desc.* \
						$(GTLANGS)/lang-crk/src/generator-dict-gt-norm.*
	@-cp $^ /opt/smi/crk/bin/


.PHONY: itwewina-install
itwewina-install: GT_COMPILE_LANGS := $(ITWEWINA_LANGS_ANALYSERS)
itwewina-install: install_langs_fsts copy-itwewina-variants

# copy-itwewina-variants


#####
##### #saantargets
#####

SAAN_LANGS_ANALYSERS      :=   sms  fin
# --with-hfst --enable-twostep-intersect --no-recursion
SAAN_LANGS_FLAGS          :=
SAAN_LANGS_LEXICA         :=   sms
SAAN_WORDS_DICTS_LEXICA   :=   finsms nobsms russms

.PHONY: saan-lexica
saan-lexica: LEX_COMPILE_LANGS := $(SAAN_LANGS_LEXICA)
saan-lexica: LEX_COMPILE_WORDS_DICTS := $(SAAN_WORDS_DICTS_LEXICA)
saan-lexica: compile_langs_lexicon compile_words_dicts_lexicon

### .PHONY: saan-combined-lexica
### saan-combined-lexica: sms2X.xml sms-all.xml
### 	mkdir -p smsc_tmp/
### 	cp -R $(GTHOME)/words/dicts/scripts ../scripts
### 	cp $^ smsc_tmp/
### 	$(SAXON) inDir=$(pwd)/smsc_tmp/ > sms-combined.xml
### 	@rm -rf smsc_tmp/
### 	@rm -rf ../scripts
### 	wc -l sms-combined.xml

.PHONY: saan
saan: GT_COMPILE_LANGS := $(SAAN_LANGS_ANALYSERS)
saan: LEX_COMPILE_LANGS := $(SAAN_LANGS_LEXICA)
saan: LEX_COMPILE_WORDS_DICTS := $(SAAN_WORDS_DICTS_LEXICA)
saan: LANGS_FLAGS := $(SAAN_LANGS_FLAGS)
saan: saan-lexica compile_langs_fsts print_complete_message

.PHONY: saan-clean
saan-clean:  GT_COMPILE_LANGS :=  $(SAAN_LANGS_ANALYSERS)
saan-clean: clean_langs_fsts

rm-saan-lexica: $(foreach xx, $(SAAN_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(SAAN_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: saan-install
saan-install: GT_COMPILE_LANGS := $(SAAN_LANGS_ANALYSERS)
saan-install: install_langs_fsts

#####
##### #vadatargets
#####

VADA_LANGS_ANALYSERS      :=   yrk fin mns
VADA_LANGS_LEXICA         :=   yrk mns
VADA_WORDS_DICTS_LEXICA   :=   finyrk mnshun

.PHONY: vada-lexica
vada-lexica: LEX_COMPILE_LANGS := $(VADA_LANGS_LEXICA)
vada-lexica: LEX_COMPILE_WORDS_DICTS := $(VADA_WORDS_DICTS_LEXICA)
vada-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: vada
vada: GT_COMPILE_LANGS := $(VADA_LANGS_ANALYSERS)
vada: LEX_COMPILE_LANGS := $(VADA_LANGS_LEXICA)
vada: LEX_COMPILE_WORDS_DICTS := $(VADA_WORDS_DICTS_LEXICA)
vada: vada-lexica compile_langs_fsts print_complete_message

.PHONY: vada-clean
vada-clean:  GT_COMPILE_LANGS :=  $(VADA_LANGS_ANALYSERS)
vada-clean: clean_langs_fsts

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
MUTER_WORDS_DICTS_LEXICA   :=   finmrj mhreng mhrrus mrjmhr mhrmrj mrjrus

.PHONY: muter-lexica
muter-lexica: LEX_COMPILE_LANGS := $(MUTER_LANGS_LEXICA)
muter-lexica: LEX_COMPILE_WORDS_DICTS := $(MUTER_WORDS_DICTS_LEXICA)
muter-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: muter
muter: GT_COMPILE_LANGS := $(MUTER_LANGS_ANALYSERS)
muter: LEX_COMPILE_LANGS := $(MUTER_LANGS_LEXICA)
muter: LEX_COMPILE_WORDS_DICTS := $(MUTER_WORDS_DICTS_LEXICA)
muter: muter-lexica compile_langs_fsts print_complete_message

.PHONY: muter-clean
muter-clean:  GT_COMPILE_LANGS :=  $(MUTER_LANGS_ANALYSERS)
muter-clean: clean_langs_fsts

rm-muter-lexica: $(foreach xx, $(MUTER_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(MUTER_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: muter-install
muter-install: GT_COMPILE_LANGS := $(MUTER_LANGS_ANALYSERS)
muter-install: install_langs_fsts

#####
##### #valkstargets
#####

VALKS_LANGS_ANALYSERS      :=   fin myv mdf deu rus est
VALKS_LANGS_LEXICA         :=   myv mdf
VALKS_WORDS_DICTS_LEXICA   :=   finmyv finmdf myvdeu deumyv engmyv myveng engmdf mdfeng mdfrus rusmyv rusmdf mdfmyv estmyv myvest

.PHONY: valks-lexica
valks-lexica: LEX_COMPILE_LANGS := $(VALKS_LANGS_LEXICA)
valks-lexica: LEX_COMPILE_WORDS_DICTS := $(VALKS_WORDS_DICTS_LEXICA)
valks-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: valks
valks: GT_COMPILE_LANGS := $(VALKS_LANGS_ANALYSERS)
valks: LEX_COMPILE_LANGS := $(VALKS_LANGS_LEXICA)
valks: LEX_COMPILE_WORDS_DICTS := $(VALKS_WORDS_DICTS_LEXICA)
valks: valks-lexica compile_langs_fsts print_complete_message

.PHONY: valks-clean
valks-clean:  GT_COMPILE_LANGS :=  $(VALKS_LANGS_ANALYSERS)
valks-clean: clean_langs_fsts

rm-valks-lexica: $(foreach xx, $(VALKS_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(VALKS_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: valks-install
valks-install: GT_COMPILE_LANGS := $(VALKS_LANGS_ANALYSERS)
valks-install: install_langs_fsts

#####
##### #sanattargets
#####

SANAT_LANGS_ANALYSERS      :=   olo fin fkv rus vep nob
SANAT_LANGS_LEXICA         :=   olo izh vep
SANAT_WORDS_DICTS_LEXICA   :=   nobfkv fkvnob finolo rusolo olorus nobfin finnob

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

.PHONY: sanat-clean
sanat-clean:  GT_COMPILE_LANGS :=  $(SANAT_LANGS_ANALYSERS)
sanat-clean: clean_langs_fsts

rm-sanat-lexica: $(foreach xx, $(SANAT_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(SANAT_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: sanat-install
sanat-install: GT_COMPILE_LANGS := $(SANAT_LANGS_ANALYSERS)
sanat-install: install_langs_fsts

#####
##### #sonadtargets
#####

SONAD_LANGS_ANALYSERS           :=   izh liv fin vep vro vot lav
SONAD_LANGS_LEXICA              :=   liv izh vep vro vot
SONAD_WORDS_DICTS_LEXICA        :=   finliv finizh lavliv finlav lavfin rusvot votrus

.PHONY: sonad-lexica
sonad-lexica: LEX_COMPILE_LANGS := $(SONAD_LANGS_LEXICA)
sonad-lexica: LEX_COMPILE_WORDS_DICTS := $(SONAD_WORDS_DICTS_LEXICA)
sonad-lexica: compile_langs_lexicon \
			  compile_words_dicts_lexicon

.PHONY: sonad
sonad: GT_COMPILE_LANGS := $(SONAD_LANGS_ANALYSERS)
sonad: LEX_COMPILE_LANGS := $(SONAD_LANGS_LEXICA)
sonad: LEX_COMPILE_WORDS_DICTS := $(SONAD_WORDS_DICTS_LEXICA)
sonad: sonad-lexica compile_langs_fsts print_complete_message

.PHONY: sonad-clean
sonad-clean:  GT_COMPILE_LANGS :=  $(SONAD_LANGS_ANALYSERS)
sonad-clean: clean_langs_fsts

rm-sonad-lexica: $(foreach xx, $(SONAD_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(SONAD_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: sonad-install
sonad-install: GT_COMPILE_LANGS := $(SONAD_LANGS_ANALYSERS)
sonad-install: install_langs_fsts

#####
##### #sanittargets
#####

##
### #sanitlexica
##

SANIT_LANGS_ANALYSERS      :=   sme fin nob sma smj spa-x-apertium
SANIT_LANGS_FLAGS          :=   --with-hfst
SANIT_LANGS_LEXICA         :=
SANIT_WORDS_DICTS_LEXICA   :=


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

smesma.xml: $(GTHOME)/words/dicts/smesma/src/
	@echo "******************************"
	@echo "** Building sme-sma lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

smasme.xml: $(GTHOME)/words/dicts/smasme/src/
	@echo "******************************"
	@echo "** Building sma-sme lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

smesmj.xml: $(GTHOME)/words/dicts/smesmj/src/
	@echo "******************************"
	@echo "** Building sme-smj lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

smjsme.xml: $(GTHOME)/words/dicts/smjsme/src/
	@echo "******************************"
	@echo "** Building sme-sma lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

spasme.xml: $(GTHOME)/words/dicts/spasme/src/
	@echo "******************************"
	@echo "** Building spa-sme lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

smespa.xml: $(GTHOME)/words/dicts/smespa/src/
	@echo "******************************"
	@echo "** Building sme-spa lexicon **"
	@echo "******************************"
	@echo "** Backup made (.bak)       **"
	@echo "******************************"
	@echo ""
	-@cp $@ $@.$(shell date +%s).bak
	$(SAXON) inDir=$^ > $@

.PHONY: sanit-lexica
sanit-lexica: fin-sme.all.xml \
			  nob-sme.all.xml \
			  sme-fin.all.xml \
			  sme-nob.all.xml \
			  smesma.xml \
			  smasme.xml \
			  smesmj.xml \
			  smjsme.xml \
			  spasme.xml \
			  smespa.xml

##
### #smeanalysers
##

.PHONY: sanit
sanit: GT_COMPILE_LANGS := $(SANIT_LANGS_ANALYSERS)
sanit: sanit-lexica compile_langs_fsts
	@echo "*********************************"
	@echo "** Built targets for sanit:    **"
	@echo "**    + sanit lexica           **"
	@echo "**    + sme analysers          **"
	@echo "**    + sma analysers          **"
	@echo "**    + smj analysers          **"
	@echo "**    + fin analysers          **"
	@echo "**    + nob analysers          **"
	@echo "**    + spa analysers          **"	
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths."
	@echo "    sudo make sanit-install"

.PHONY: sanit-install
sanit-install: GT_COMPILE_LANGS := $(SANIT_LANGS_ANALYSERS)
sanit-install: install_langs_fsts

.PHONY: sanit-clean
sanit-clean:  GT_COMPILE_LANGS :=  $(SANIT_LANGS_ANALYSERS)
sanit-clean: clean_langs_fsts

rm-sanit-lexica:
	@rm -rf fin-sme.all.xml nob-sme.all.xml sme-fin.all.xml sme-nob.all.xml \
		smesma.xml smasme.xml smesmj.xml smjsme.xml spasme.xml smespa.xml

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

BAAKOEH_LANGS_ANALYSERS      :=   sma nob
BAAKOEH_LANGS_LEXICA         :=
BAAKOEH_WORDS_DICTS_LEXICA   :=

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
	@rm -rf sma-nob.all.xml nob-sma.all.xml smesma.xml smasme.xml

.PHONY: baakoeh-install
baakoeh-install: GT_COMPILE_LANGS := $(BAAKOEH_LANGS_ANALYSERS)
baakoeh-install: install_langs_fsts

.PHONY: baakoeh
baakoeh: GT_COMPILE_LANGS := $(BAAKOEH_LANGS_ANALYSERS)
baakoeh: baakoeh-lexica compile_langs_fsts
	@echo "*********************************"
	@echo "** Built targets for baakoeh:  **"
	@echo "**    + baakoeh lexica         **"
	@echo "**    + sma analysers          **"
	@echo "**    + sme analysers          **"
	@echo "**    + nob analysers          **"
	@echo "*********************************"
	@echo ""
	@echo "Now install analysers in expected paths"
	@echo "    make baakoeh-install"

.PHONY: baakoeh-clean
baakoeh-clean:  GT_COMPILE_LANGS :=  $(BAAKOEH_LANGS_ANALYSERS)
baakoeh-clean: clean_langs_fsts

#####
##### #kyvtargets
#####

KYV_LANGS_ANALYSERS      :=   kpv fin udm hun koi rus est
KYV_LANGS_LEXICA         :=   udm kpv koi
KYV_WORDS_DICTS_LEXICA   :=   finkpv udmkpv kpvudm udmfin finudm udmhun hunudm koikpv kpvkoi kpvrus ruskpv estudm

.PHONY: kyv-lexica
kyv-lexica: LEX_COMPILE_LANGS := $(KYV_LANGS_LEXICA)
kyv-lexica: LEX_COMPILE_WORDS_DICTS := $(KYV_WORDS_DICTS_LEXICA)
kyv-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: kyv
kyv: GT_COMPILE_LANGS := $(KYV_LANGS_ANALYSERS)
kyv: LEX_COMPILE_LANGS := $(KYV_LANGS_LEXICA)
kyv: LEX_COMPILE_WORDS_DICTS := $(KYV_WORDS_DICTS_LEXICA)
kyv: kyv-lexica compile_langs_fsts print_complete_message

.PHONY: kyv-clean
kyv-clean:  GT_COMPILE_LANGS :=  $(KYV_LANGS_ANALYSERS)
kyv-clean: clean_langs_fsts

rm-kyv-lexica: $(foreach xx, $(KYV_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(KYV_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: kyv-install
kyv-install: GT_COMPILE_LANGS := $(KYV_LANGS_ANALYSERS)
kyv-install: install_langs_fsts copy_molodtsov copy_forPermyak

.PHONY: copy_molodtsov
copy_molodtsov: $(GTLANGS)/lang-kpv/src/analyser-dict-gt-desc-molodtsov.xfst
	cp $^ /opt/smi/kpv/bin/analyser-dict-gt-desc-molodtsov.xfst

.PHONY: copy_forPermyak
copy_forPermyak: $(GTLANGS)/lang-kpv/src/analyser-dict-gt-desc-permyak.xfst
	cp $^ /opt/smi/kpv/bin/analyser-dict-gt-desc-permyak.xfst

#####
##### #bahkogirrjetargets
#####

BAHKOGIRRJE_LANGS_ANALYSERS      :=   sje  nob
# --with-hfst --enable-twostep-intersect --no-recursion
BAHKOGIRRJE_LANGS_FLAGS          :=
BAHKOGIRRJE_LANGS_LEXICA         :=   sje
BAHKOGIRRJE_WORDS_DICTS_LEXICA   :=   sje2X

.PHONY: bahkogirrje-lexica
bahkogirrje-lexica: LEX_COMPILE_LANGS := $(BAHKOGIRRJE_LANGS_LEXICA)
bahkogirrje-lexica: LEX_COMPILE_WORDS_DICTS := $(BAHKOGIRRJE_WORDS_DICTS_LEXICA)
bahkogirrje-lexica: compile_langs_lexicon compile_words_dicts_lexicon

.PHONY: bahkogirrje
bahkogirrje: GT_COMPILE_LANGS := $(BAHKOGIRRJE_LANGS_ANALYSERS)
bahkogirrje: LEX_COMPILE_LANGS := $(BAHKOGIRRJE_LANGS_LEXICA)
bahkogirrje: LEX_COMPILE_WORDS_DICTS := $(BAHKOGIRRJE_WORDS_DICTS_LEXICA)
bahkogirrje: LANGS_FLAGS := $(BAHKOGIRRJE_LANGS_FLAGS)
bahkogirrje: bahkogirrje-lexica compile_langs_fsts print_complete_message

.PHONY: bahkogirrje-clean
bahkogirrje-clean:  GT_COMPILE_LANGS :=  $(BAHKOGIRRJE_LANGS_ANALYSERS)
bahkogirrje-clean: clean_langs_fsts

rm-bahkogirrje-lexica: $(foreach xx, $(BAHKOGIRRJE_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(BAHKOGIRRJE_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: bahkogirrje-install
bahkogirrje-install: GT_COMPILE_LANGS := $(BAHKOGIRRJE_LANGS_ANALYSERS)
bahkogirrje-install: install_langs_fsts


#####
##### #focailtargets
#####

### When starting a new project, copy this whole section (down to
### #/focailtargets), and change the following settings. Then, be sure to
### replace all instances of FOCAIL and focail in variables and target names
### with the PROJNAME.

# These are the ISOs of the languages to compile from GTLANGS/lang-xxx/
FOCAIL_LANGS_ANALYSERS           := gle

# OPTIONAL: enable miscellaneous ./configure flags
# FOCAIL_LANGS_FLAGS             :=   --with-hfst

# Compile the lexicon from within GTLANGS/src/fst/stems/*.xml

FOCAIL_LANGS_LEXICA              :=

# Compile the lexicon from a directory within GTHOME/words/dicts/
FOCAIL_WORDS_DICTS_LEXICA        :=   gleeng

.PHONY: focail-lexica
focail-lexica: LEX_COMPILE_LANGS := $(FOCAIL_LANGS_LEXICA)
focail-lexica: LEX_COMPILE_WORDS_DICTS := $(FOCAIL_WORDS_DICTS_LEXICA)
focail-lexica: compile_langs_lexicon \
			  compile_words_dicts_lexicon

.PHONY: focail
focail: GT_COMPILE_LANGS := $(FOCAIL_LANGS_ANALYSERS)
focail: LEX_COMPILE_LANGS := $(FOCAIL_LANGS_LEXICA)
focail: LEX_COMPILE_WORDS_DICTS := $(FOCAIL_WORDS_DICTS_LEXICA)
focail: focail-lexica compile_langs_fsts print_complete_message

rm-focail-lexica: $(foreach xx, $(FOCAIL_LANGS_LEXICA), $(xx)-all.xml) \
				 $(foreach yy, $(FOCAIL_WORDS_DICTS_LEXICA), $(yy).xml)
	@rm -rf $^

.PHONY: focail-install
focail-install: GT_COMPILE_LANGS := $(FOCAIL_LANGS_ANALYSERS)
focail-install: install_langs_fsts


.PHONY: focail-clean
focail-clean:  GT_COMPILE_LANGS :=  $(FOCAIL_LANGS_ANALYSERS)
focail-clean: clean_langs_fsts

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


 # | sed 's/\./   /g' | cut -f 1 | sort -u > dicts.tmp

# This will store all old dictionaries with a particular suffix and
# *.xml.bak in an archive. Each archive will be expanded and
# recompressed if new files are found. We need backups, but they take up
# a lot of space in some cases
#
.PHONY: collect-backups
collect-backups: BACKS := $(shell ls -c1 *.xml.*.bak | sed "s/\.xml.[0-9]*\.bak//" | sort | uniq)
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
	 saanih \
	 sanit \
	 sonad \
	 baakoeh \
	 kyv \
	 muter \
	 bahkogirrje
	@echo $(TARGET_DIR)

.PHONY: all-lexica
all-lexica: baakoeh-lexica \
	kyv-lexica \
	muter-lexica \
	saan-lexica \
	saanih-lexica \
	sanat-lexica \
	sonad-lexica \
	sanit-lexica \
	vada-lexica \
	valks-lexica \
	bahkogirrje-lexica
	@echo $(TARGET_DIR)
