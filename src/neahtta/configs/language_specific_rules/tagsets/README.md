# Tagsets

Tagsets are necessary for constructing certain types of rules for manipulating
lexical information and morphological information, either for generating forms,
or analyzing input, or even determining how entries should be displayed...
However, tagsets crucially operate on morphological analyzer output. Tagsets
are particularly integral in defining paradigms.

Tagsets are file based because this makes it easier to duplicate them for
language variants, or share languages across dictionary instances--
particularly majority languages, for which it is easy to forget to check
settings for when they are used in multiple installations.

## Tagset files

Each language has its own set of tagsets, and these are defined in a file in:

    configs/language_specific_rules/tagsets/

The filename must be `ISO.tagset`, where ISO is a variable for the 3-character
language ISO (even for languages like `se`, which should be listed in this
directory as `sme`).

The file format is YAML, and all that is permitted here is key-value settings,
where the key is the name of the tagset, and the value is a list of tags that
fit into this tagset.

## Example

Here's an example of some tagsets from `sme`:

    pos:
     - "N"
     - "V"
     - "A"
     - "Pr"
     - "Po"
     - "Num"
     - "CS"
     - "CC"
     - "pron."
     - "subst."
     - "verb"
     - "adj."
     - "konj."
    type: 
     - "NomAg"
     - "G3"
     - "aktor"
     - "res."
     - "Prop"
     - "prop."
    number: ["Sg", "Pl"]

Note that YAML allows you to define lists in multiple ways, and strings may be
quoted or non-quoted, however, it is often a good idea to quote them anyway,
because certain values like `no` and `yes` may be translated to boolean values
`True` and `False`, instead of being used as plain strings.

The above example also shows the two alternate list formats, one with brackets,
and the other with hyphens.

Note that comments are also allowed (marked with `#`), and it may be useful
to document some sets as needed.

## More YAML documentation

http://en.wikipedia.org/wiki/YAML#Lists

