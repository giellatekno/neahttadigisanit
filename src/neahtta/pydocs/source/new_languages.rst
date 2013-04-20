Adapting NDS to new languages
-----------------------------

How do programmers adapt NDS to support new languages?

The overall desire is that most of the basic functionality is good
enough to support adding new lexicons and new lexicon types, as well as
new types of morphological tools.

Most of this documentation for now concerns adding new languages that
fit into the Giellatekno FST format, and the Giellatekno lexicon format. 

What to adapt
-------------

Different lexica and different languages have different needs for
presenting entries. Some typical considerations that need to be
addressed in code are:

 * Do the lexicon and the morphology line up for basic things like part
   of speech? If they cannot be changed, `lexicon overrides` will be
   required.

 * Is there anything in the lexicon that determines what type of
   paradigm must be generated? If so, `generation overrides` will be
   required.

 * Is there a requirement to display a specific text attribute from the
   lexicon for a particular language, or a particular part of speech? If
   so, `morpholexicon overrides` will be necessary.

Lexicon overrides
-----------------

TODO: what decorator functions?

TODO: display some sample usages from sme and sma.

Morphology overrides
--------------------

TODO: what decorator functions?

TODO: display some sample usages from sme and sma.

Morpho-lexicon overrides
------------------------

TODO: what decorator functions?

TODO: display some sample usages from sme and sma.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


