# Language specific rules

Each language has its own needs. Within this directory, you will find several places
to configure a language for use in Neahttadigisánit.

 1.) Tagsets (`tagsets/`)
 2.) Paradigms (`paradigms/`)
 3.) Paradigm contexts (`paradigms/*.context`)
 4.) Python-based morphological and lexical overrides (`ISO.py`)

All of these are meant for easy editing, but in practice, those that are not
Python files are the easiest, and linguists are encouraged to take a look and
feel welcome to make edits. Since the Python-files are somewhat obtuse to edit
for linguists, the eventual goal is that any linguistic configuration necessary
within these files will be transitioned to a more user-friendly format.

Each of these are documented in their relevant directories, but a quick overview here:

 * **Tagsets** - one language per file Tagset definition.
 * **Paradigms** - one directory per language, and one paradigm per file; uses
   [Jinja templates][jinja] to structure paradigms, and [YAML][yaml]
   to produce conditions for their use. Most templates will be simple, but
   `sme` contains some more advanced examples.
 * **Paradigm contexts** - Allows for added control over display of generated
   wordforms, adding helpful pronoun, adverb contexts, etc.
 * **Python-based overrides** - These are more varied in what they do:
   - Pregenerated form selection (generator override, lexicon -> paradigm)
   - Morphology <-> Lexicon tag synchronization
   - Autocomplete filtering
   - Lexicon entry lookup filtering (excluding entries without `usage="vd"`)
   - Entry display formatting (a great candidate for making a template-based solution,
     see `templates/README.md` for ideas)

  [jinja]: http://jinja.pocoo.org/docs/templates/
  [yaml]: http://en.wikipedia.org/wiki/YAML
