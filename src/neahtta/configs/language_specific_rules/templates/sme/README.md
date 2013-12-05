# This doesn't work.

So far it's just some ideas of how to potentially interact with
formatting lexicon entries, and intended to be more understandable.
Likely some things need work, but as ideas come up I'll start writing
them down.

## Language folder structure

Each folder is a language, named by the ISO. Each file is a combination
of YAML and Jinja (but this could change too-- I could see YAML and XSLT
snippets). Filenames may be whatever, with the exception of 'default',
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

