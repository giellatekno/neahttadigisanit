# About configs

**Partly outdated!**: Trond Ty: I have updated this file in August 2026, but it might still contain some outdated info.

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

### 1.) Configure FSTs and lexicon.

**Intended**: Programmers

#### FSTs

FSTs are by default installed from Apertium nightly. If one wants to add e.g. South Saami, all that is needed is to install it from apt: `sudo apt install giella-sma`. The server is set up to update these from the Apertium repository every night.

The files are located at `/usr/share/giella/<iso>/`. These paths must be added to the Morphology section of the yaml file, see the example:
```
sma:
    tool: *HFST-LOOKUP
    file: '/usr/share/giella/sma/analyser-dict-gt-desc.hfstol'
    inverse_file: '/usr/share/giella/sma/generator-dict-gt-norm.hfstol'
    format: 'hfst'
    options:
      compoundBoundary: "+Cmp#"
      # Grammatical tags which have their own lexicon entries
      # that should be presented if they are part of the analysis
      tags_in_lexicon: ['Der', 'VAbess', 'VGen', 'Ger', 'Comp', 'Superl', 'Actio']
```

If the language does not yet exist in Apertium nightly, consider asking for it to be added. If that is not possible, you may compile the FSTs yourself and place them in a suitable directory pointed to by the `file` and `inverse_file` parameters.

#### Lexicon

Lexica are compiled using the `merge_giella_dicts.py` script found in `giella-core/dicts/scripts/`. The `nds compile` command figures out the location of the file based on the `source`, `target` and `dict_source` variables in the Dictionaries section of the yaml file.

`dict_source` is set to 
 - `multi` for `dict-<source-iso>-mul` repos, 
 - `lang` for `lang-<source-iso>` repos, or
 - `repo: <repo-name>` for custom repos
If the source repo is `dict-<source>-<target>`, then `dict_source` can be dropped from the config.

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

```
sma:
    tool: *HFST-LOOKUP
    file: '/usr/share/giella/sma/analyser-dict-gt-desc.hfstol'
    inverse_file: '/usr/share/giella/sma/generator-dict-gt-norm.hfstol'
    format: 'hfst'
    options:
      compoundBoundary: "+Cmp#"
      # Grammatical tags which have their own lexicon entries
      # that should be presented if they are part of the analysis
      tags_in_lexicon: ['Der', 'VAbess', 'VGen', 'Ger', 'Comp', 'Superl', 'Actio']
```

Where YYY is the language ISO path.

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


### 3.) Define language names and translation strings

**Intended**: Linguists

Open the file `configs/language_names.py`. Here you will need to add the
language ISO to several variables. Save when done, and be sure to check
in in git.

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

### 4.) Define tagsets, and paradigms, user-friendly tag relabels

**Intended**: Linguists

If you wish to have paradigms visible in the language, you will need two
things: 

 * `Tagsets` files: `configs/language_specific_rules/tagsets/README.md`
 * `.paradigm` files: `configs/language_specific_rules/paradigms/README.md`
 * `.context` files: `configs/language_specific_rules/paradigms/README.md`
 * `.relabel` files: `configs/language_specific_rules/user_friendly_tags/README.md`

The easiest means of course is to look at existing languages and copy
what they do.

When done with these steps, be sure to add the new files and directories
to git and check them in.

### 5.) Paradigm bonus material: wordform contexts

**Intended**: Linguists

Paradigm contexts give additional information to users about how
wordforms are intended to be used.  Information about these is also
maintained in the paradigms readme.

    configs/language_specific_rules/paradigms/README.md



