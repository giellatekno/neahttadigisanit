# This also doesn't work.

Managing paradigms and generation is currently not a straightforward
task, but it needs to be, and a file-based approach might work well as
long as the rules are all read at runtime and no further interactions
with the files are needed.

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

Typically, rules that only apply to a subset will not require some sort
of ordering of the rules in order to get them to be applied properly,
i.e., there is hopefully no overlap in subsets. If there is, filesystem
ordering could be used to get out of this.

## Paradigm file structure

Paradigm files are structured the same as templates: one part is YAML,
and the other part is data in Jinja form. Essentially what this says is,
if the first part's (YAML) conditions are matched, then we use the
paradigm following.

    analyzer:
      pos: N
    lexicon:
      pos: N
      type: Prop
    --
    {{ lemma }}+N+Prop+Sem/Plc+Sg+Gen
    {{ lemma }}+N+Prop+Sem/Plc+Sg+Ill
    {{ lemma }}+N+Prop+Sem/Plc+Sg+Loc


## Analyzer conditions

Conditions that are possible to match on are set up in a variety of
ways. Analyzer conditions may be specified in the `analyzer` key,
and each key under that may be a tagset and a value, or a whole tag:

    analyzer:
      pos: V
      infinitive: true

    ... is the same as ...

    analyzer:
      tag: V+Inf

    ... or ... 

    analyzer:
      tag: 
        - V+Inf1
        - V+Inf2

Either a value may be specified, or boolean 'true', which stands for
'any member of the tag set is present'. A list may also be specified, 
which is in effect a kind of locally defined tagset.

One other key that might be used for the analyzer is 'lemma', which is
also present for lexicon, assuming that you only want the rule to apply
to a specific lemma.

    analyzer:
      lemma: "diehtit"

## Lexicon conditions

The lexicon is also usable for providing conditions for a particular
paradigm. Some predefined keys are available, and it is also possible
to use XPATH statements to test against individual XML entries.

    lexicon:
      lemma: "diehtit"
      pos: "V"
      val: "TV"

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

And you may also refer to the lexicon match result:

    {{ lemma }}+N+Prop+Sem/{{ lexicon.sem_type }}+Sg+Nom

## Things to think about

Pregenerated paradigms could be accomplished by a template, but it would
be fairly complex, and thus would require good access to `lxml` nodes
without lots of complex template tags and custom filters. 

For ease of template use, lots of string(normalize-space()) will need to
be done on certain XPATH-provided variables.
