# This doesn't work.

So far it's just some ideas of how to potentially interact with
formatting lexicon entries, and intended to be more understandable.
Likely some things need work, but as ideas come up I'll start writing
them down.

## Implementation ideas (further thinking on the below)

Maybe each entry needs one main template, from which all sub-templates are
included, thus each language can define its own structure if it wants.

Need a default directory for everything, for which individual files are
able to be overridden if they aren't present-- which should also go for
the main default template.

Each of these sets of templates needs to go in a general-to-specific way:

    templates/
        entry.template
        entry.notes.template
        definition.template
        definition.notes.template
        paradigm.template

        sanit/
            entry.template

            sme/
                definition.template
                paradigm.template

            nob/
                definition.template
                paradigm.template

        vada/

            yrk/

            fin/

So, the highest level overrides the sub-levels. These can go
language-by-language, which also means it's possible to define a
language presentation globally, but then override it in individual
sub-projects as necessary.

In order to handle the overriding of individual parts, the main template
will need to call each part by a custom tag, not {% include %}, because
managing the path alterations for {% include %} statements would get a
bit tricky.

Also need to assume that someone will want to alter the types of parts
that are available and be able to call them without crazy alterations to
Python.

TODO: languages may need their own specific macros-- this should be
possible to define local ones that are included with higher-level
macros.

TODO: how will this interact with sme.py, sma.py, etc.? Functions there
should be retired eventually, and most of these that alter what is
rendered, act on the string level. Other things, like the linking that
occurs in 'hverandre' could also be modified to use templates more (as
they should), while maybe sme.py overrides and such should be moved
to files within this directory structure, and instead be used to define 
additional template contexts

## Language folder structure

Each folder is a language, named by the ISO. Each file is a combination
of YAML and Jinja (but this could change too-- I could see YAML and XSLT
snippets). The delimeter for that is '--' on a blank line. Hopefuly that
won't pop up at all in an actual template.

Filenames may be whatever, with the exception of 'default',
which is the 'whatever' case for when no other templates apply.

Filename suffixes are used to determine what 'field' in the definition
the template applies to.

Each translation in the list of search results looks like this: 

   {entry}                                            {paradigm}
  
   {entry.notes}
  
    1. {definition}
  
       {definition.notes}
  
    2. {definition}
  
       {definition.notes}
  
    3. {definition}
  
       {definition.notes}

 * .entry - the lemma field

 * .entry.notes - notes pertaining to the entry that go beyond
    annotations, examples, etc.

 * .definition - definitions for the entry

 * .definition.notes - examples, and whatever other things

 * .paradigm - paradigms to generate and display for a given entry

## YAML Parameters

This is the trickier part I am less certain of.

YAML parameters allow for: 

 * specifying what the entry has to match
 * specifying what morphology has to match from the analyser
 * specifying what additional arguments should be pulled out from
   entries via XPATH

So far...

    description: "Documentation not shown to end-users"
    entry_template_context:
      pos: "./e/lg/l/@pos"
      type: "./e/lg/l/@type"
      region: "./tg/t/@reg"
    lexicon_filters:
      pos: N
      type: Prop
      sem_type: plc
    morphology_filters:
      pos: N
      type: Prop

`entry_template_context` for specifying additional entry arguents to
pull out via xpath.

`lexicon_filters` should probably be only specific to entrie, because
definitions have different needs. Also, where do we define how "pos" is
pulled from an entry?

`morphology_filters` the analyses from the morphology lookup must also
match this.

## Jinja

Allows for some more conditional stuff, but more or less the goal is to
format to HTML markup.

May need some additional filters, which could maybe remove the need to set
up arguments in entry_args to get things out... i.e.: 

    {{ entry|xpath:"./e/lg/l/@pos" }}

But then obviously this makes the templates look more cluttered. Perhaps
both options available.

People writing templates should not have to think about translating tags
to localisation languages, thus if someone selects to use tags as part
of the template, these tags need to be some class that automatically
handles that when called by a template tag.

! Trick though, when tags come from lexicon, they're a result of xpath
queries, thus it would be tricky to decide what is a tag and what is
not, so probably this does need to be explicit, always; assuming things
are strings unless otherwise noted.

