# Contents

 * Paradigm generation
 * Paradigm wordform context

# Paradigm generation

Paradigms are managed by a file and directory structure.

## Paradigm folder structure

    paradigms/sme/common_nouns.paradigm
    paradigms/sme/proper_nouns.paradigm
    paradigms/sme/paradigm_group/foo.paradigm
    paradigms/sme/paradigm_group/bar.paradigm

Paradigms can be ordered however in each directory, and may be grouped
for convenience into other folders. A language typically won't need
many, and usually there will be one base paradigm for a part of
speech from which additional paradigms apply to subsets of words in
this part of speech.

Currently, there is no explicit setting for ordering the rules, and ordering is
determined by the complexity of the rules that match a given word and entry.
Thus, if one rule looks for `pos`, `valence` and `context`, and another
only looks for `pos` and `valence`, the former will be applied if both
match.

Symlinks are tolerated, so if multiple language variants need to use the same
rule set, simply make a symlink between the directories.

## Paradigm file structure

Paradigm files are structured in the following wa: one part is YAML, and the
other part is data in Jinja form. Essentially what this says is, if the first
part's (YAML) conditions are matched, then we use the paradigm following.

    name: "Proper noun paradigm."
    description: |
      Generate the proper noun if the entry contains sem_type="Prop" or
      "prop"
    morphology:
      pos: "N"
    lexicon:
      XPATH:
        type: ".//l/@type"
      sem_type: 
        - "Prop"
        - "prop"
    --
    {{ lemma }}+N+Prop+Sem/Plc+Sg+Gen
    {{ lemma }}+N+Prop+Sem/Plc+Sg+Ill
    {{ lemma }}+N+Prop+Sem/Plc+Sg+Loc


## Analyzer conditions

Conditions that are possible to match on are set up in a variety of
ways. Analyzer conditions may be specified in the `analyzer` key,
and each key under that may be a tagset and a value, or a whole tag:

    morphology:
      pos: "V"
      infinitive: true

    ... is the same as ...

    morphology:
      tag: "V+Inf"

    ... or ... 

    morphology:
      tag: 
        - "V+Inf1"
        - "V+Inf2"

Either a value may be specified, or boolean 'true', which stands for
'any member of the tag set is present'. A list may also be specified, 
which is in effect a kind of locally defined tagset.

One other key that might be used for the analyzer is 'lemma', which is
also present for lexicon, assuming that you only want the rule to apply
to a specific lemma.

    morphology:
      lemma: "diehtit"

## Lexicon conditions

The lexicon is also usable for providing conditions for a particular
paradigm. Some predefined keys are available, and it is also possible
to use XPATH statements to test against individual XML entries.

    lexicon:
      XPATH:
        sem_type: ".//l/@sem_type"
      sem_type: "Plc"
      
    lexicon:
      XPATH:
        sem_type: ".//l/@sem_type"
      sem_type: 
        - "Plc"
        - "Something"

    lexicon:
      XPATH:
        ader: ".//l/@ader"
      ader: true

  Either a value may be specified, or boolean 'true', which stands for
  'the attribute is defined on the lemma node'. A list may also be specified.
  Only specifying the XPATH is possible, but does not help NDS pick the correct
  paradigm file. For that to work, possible values must be specified.

## Conditions together

Operating together, what the conditions say is that for any
user-inputted wordform, if the analyzer rules find a matching analysis, 
and the lexicon rules find a matching lexicon entry, then the paradigm
will be used for the entries where these align.

## Paradigm definition

Paradigm definition is mostly plaintext, but since it is a template, it
is possible to do all sorts of template operations.

    {{ lemma }}+N+Sg+Nom
    {{ lemma }}+N+Sg+Acc

Certain variables are available by default:

  - `lemma`

## Things to think about

* Pregenerated paradigms could be accomplished by a template, but it would
  be fairly complex, and thus would require good access to `lxml` nodes
  without lots of complex template tags and custom filters. 

# Paradigm contexts

For now this isn't entirely in line with the way Paradigm Generation
works, but it should be good enough for linguists to see the pattern and
work accordingly.

`.context` files in each directory control what is displayed with the
generated wordform. The filename may be anything, so long as the suffix
is `.context`. For convenience, `sme` and `sma` match filenames between
paradigms and context, but there is no need to do so, and one `.context`
file could be used for everything.

## File structure

Context files are simply a YAML list, and each item is a dictionary
with the following keys:
 
 * `entry_context` - matches the `@context` attribute on each `<l />`
   node. Set to a string, or None
 * `tag_context` - matches the tag used in generation. String. Must be
   set to something, as none would overgenerate.
 * `template` - jinja-format string, which accepts certain variables:
   + `word_form` - inserts the wordform
   + `context` - inserts the context (usually not necessary)

Some examples:

    - entry_context: "sii"
      tag_context: "V+Ind+Prs+Pl3"
      template: "(odne sii) {{ word_form }}"

The above would thus generate:

    (odne sii) deaivvadit

Example without entry_context:

    - entry_context: None
      tag_context: "V+Ind+Prs+Sg1"
      template: "(daan biejjien manne) {{ word_form }}"

Note the lack of quotes around `None`.

Otherwise, see the checked in files for more examples.

### Programmer todos

TODO: function currently assumes tag separator is +, use the tag
separator defined in morphology

TODO: maybe consider making this work similarly to paradigm generation,
so that tagsets may be used if needed.

