# About configs

Because paths in the configs likely must change depending on the place the
service is running, the .in files are the only things checked in. Make a copy
and change the necessary paths to FSTs and such, and run the service with that.
If there are changes to paradigms and such, be sure to check those in.

Configs are written in .yaml, and should be fairly self explanatory. See 
sample.config.yaml.in for explanations of the various options.

## Adding a new language

So far the process is a little complex, but there are things that can be
done mostly by linguists once the basic structure is in place. In each
following section, I'll mark who the role is best suited for, thus it's
clearer where work can be shared.

This following process assumes that there is already a service existing
to which a new language pair is being added.

### 1.) Establish a build process for the FSTs and lexicon.

**Intended**: Programmers

#### FSTs

Assuming that the language uses the `langs/` infrastructure, adding
another to a dictionary set's build process is easy. Find the targets
for the dictionary set, for example, `kyv` and `kyv-install`, and add
the language ISO to the variable `GT_COMPILE_LANGS` for these
targets.

    .PHONY: baakoeh-install
    baakoeh-install: GT_COMPILE_LANGS := sma nob
    baakoeh-install: install_langs_fsts 

    .PHONY: baakoeh
    baakoeh: GT_COMPILE_LANGS := sma nob
    baakoeh: baakoeh-lexica compile_langs_fsts
    [... snip ...]

The dependencies for these will then automatically build, using as much
of the `langs/` build infrastructure as possible.

These targets will build analysers as usual, but the `*-install` targets
are there as a convenience for when overwriting the analysers in
`/opt/smi/` is allowed. **Be careful** with this though, because with
language sets like `sánit` and `baakoeh` which are very much in
production mode now, there may be some unintended consequences.

In any case, the targets that these will write to are
dictionary-specific, and will not overwrite analysers for other
projects.

    /opt/smi/LANG/bin/dict-LANG.fst
    /opt/smi/LANG/bin/dict-iLANG-norm.fst
    /opt/smi/LANG/bin/some-LANG.fst

##### Troubleshooting

If you do not succeed in getting these make targets to work with a new
language, run the process manually. It might be that `make distclean`
needs to be run once within the language directory, and then things will
work.

#### Lexicon

Editing the Makefile is a little tricky. You will need to add a target
for the lexicon file or files. 

Lexica are compiled using a `Saxon` process, and the Makefile contains
some variables that can be used as shortcuts. For languages using
`langs/` infrastructure for the lexicon, the best option is the
following:

    ZZZ-all.xml: $(GTHOME)/langs/ZZZ/src/morphology/stems/*.xml
	    @echo "**************************"
	    @echo "** Building ZZZ lexicon **"
	    @echo "**************************"
	    @echo "** Backup made (.bak)   **"
	    @echo "**************************"
	    @echo ""
	    -@cp $@ $@.$(shell date +%s).bak
	    mkdir ZZZ
	    cp $^ ZZZ/
	    $(SAXON) inDir=$(pwd)/ZZZ/ > ZZZ-all.xml
	    rm -rf ZZZ/

The above makes a copy of the XML files, and then uses the Saxon process
to compile them all into one file, with no additional processing.

This process will be the same if the lexica are in `main/words/dicts/`, 
however some languages there have multiple subdirectories that need to
be copied before the Saxon process is run.

Make note of the filename that you intend to output this to, and add it
to the language installation's lexicon target, for example,
`kyv-lexica`, `muter-lexica`; and also the remove target
(`rm-kyv-lexica`).

### 2.) Edit the .yaml file for new FSTs and Dictionaries

**Intended**: Programmers, linguists

Realistically anyone can do this as long as the build process is
working, since most of this should be a cut-and-paste job.

Once you're done, save the file and attempt to restart the service.

If everything seems to be working, do not check in the config file
itself, but copy the values to `INSTANCE.config.yaml.in`, and check that
in. This is simply so that no incoming updates to config files will
destroy existing production configs.

#### `Morphology` section

This needs to have the paths to the new analysers, for each language
ISO. Follow one of the existing languages and adjust the values as
necessary. If any language variants (mobile spellrelax) need to be
included, a good idea is to use the language ISO as the key, but with
one letter appended, i.e., `udm` for mobile would be `udmM`.

In any case, the morphology section should contain a new entry like the
following:

    YYY:
      tool: *LOOKUP
      file: [*OPT, '/YYY/bin/dict-YYY.fst']
      inverse_file: [*OPT, '/YYY/bin/dict-iYYY-norm.fst']
      format: 'xfst'
      options:
        compoundBoundary: "+Use/Circ#"
        derivationMarker: "+Der"
        tagsep: '+'
        inverse_tagsep: '+'

Where YYY is the language ISO path. Note the weird way that forming
paths with aliases is handled here in YAML, they may be strings or
lists, and if they are lists, they will be automatically concatinated
into strings. This must be done because YAML does not allow string 
concatenation with aliases/variables.

#### `Languages` section

Add a new entry for the language iso to this list.


#### `Dictionaries` section

Here, add a new item to the list of dictionaries, relative to the
`neahtta` path, i.e., `dicts/file-name.xml`.

    Dictionaries:

      # [... snip ...]

      - source: udm
        target: hun
        path: 'dicts/udm-all.xml'

If any language variants, mobile spellrelax, need to be included, this
is the place to define them. Note that for the `type` setting, the
values `standard` and `mobile` are special. Only use this for mobile
spell-relax. If the type of variant is something else, like handling
multiple orthographies, use another value.

The variant marked with `mobile` will be the variant that is
automatically displayed if a user navigates to the page via mobile
browser.

`short_name` for each variant must be set to the same value as the FST,
so, `"sme"`, or `"SoMe"`, or `udmM`.

`description` will be displayed to users.

  - source: sme
    target: nob
    path: 'dicts/sme-nob.all.xml'
    input_variants:
      - type: "standard"
        description: "Standárda (<em>áčđŋšŧž</em>)"
        short_name: "sme"
      - type: "mobile"
        description: "Sosiála media (maiddái <em>acdnstz</em>)"
        short_name: "SoMe"


#### `TagTransforms` section

**Intended**: Linguists

The purpose of this section is to translate tag pieces to a
user-friendly format, and alternatively, remove them from being
displayed. See other language configurations for an idea, but following
is a short example.

    TagTransforms:
      # (source_language_fst, user_interface_language):
      #  "FSTOUTPUT": "user sees this"
      #  "DO_NOT_DISPLAY": ""

      (sme, nob):
        "V": "v."
        "N": "s."
        "A": "adj."

      (fin, sme):
        "V": "v."
        "N": "n."

Each piece of the tag will be split by the tag separater defined in the
Morphology section for the language. Empty values may be used to avoid
displaying this piece of the tag, for instance when the FST needs to
output a tag for certain display rules or paradigm generation, but the
user does not need to see these anyway. 

* language variant names in language_names

### 3.) Define language names and translation strings

**Intended**: Linguists

Open the file `configs/language_names.py`. Here you will need to add the
language ISO to several variables. Save when done, and be sure to check
in in SVN.

#### NAMES

Here we define the name in English, so that it will be available for
translation to any interface languages.

    ('sme', _(u"North Sámi")),

The most easy way is to copy one existing line, and replace the contents
of the strings. If you're unfamiliar with Python, be careful not to
remove any underscores around the strings, and only edit the contents.

The first value should be the language ISO, **or** the language variant
(`SoMe`, `udmM`, `kpvS`, etc.)

#### LOCALISATION_NAMES_BY_LANGUAGE

Here we have the ISO and the language's name in the language.

    ('sme', u"Davvisámegiella"),

Again, copy and paste a line, and only edit the strings.

#### ISO_TRANSFORMS

If the language has a two-character ISO as well as a three-character
ISO, we must have these defined here.

    ('se', 'sme'),
    ('no', 'nob'),
    ('fi', 'fin'),
    ('en', 'eng'),

### 4.) Define tagsets, and paradigms

**Intended**: Linguists

If you wish to have paradigms visible in the language, you will need two
things: 

 * `Tagsets`
 * `.paradigm` files

For more information on these, see the readme in
`configs/language_specific_rules/README.md`, and
`configs/language_specific_rules/paradigms/README.md`.

The easiest means of course is to look at existing languages and copy
what they do.

When done with these steps, be sure to add the new files and directories
to SVN and check them in.

### 5.) Paradigm bonus material: wordform contexts

**Intended**: Linguists

Paradigm contexts give additional information to users about how
wordforms are intended to be used.  Information about these is also
maintained in the paradigms readme.

    configs/language_specific_rules/paradigms/README.md

