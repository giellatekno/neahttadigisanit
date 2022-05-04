""" Functionality for registering search lookup types, throughout the
app as well as in project-specific files. Ex.)

... in: itwewina.config.yaml

  - source: eng
    target: crk
    path: 'dicts/engcrk.xml'
    search_variants:
     - type: "substring_match"  # <== this must match custom lookup type
       path: "dicts/engcrk.xml"
       description: "match on substrings"
       example: "do -> do, undo"


... in: language_specific_configs/crk.py

    >>> @search_types.add_custom_lookup_type('substring_match')
    >>> class SubstringLookups(XMLDict):
    >>>     pass

See lexicon.custom_lookups.py for implementation notes on these custom
classes.

NB: you can also override default lookup types in this way, since they are simply registered with 'regular'.

"""


class SearchTypes(object):
    """ An object for collecting search types. Initialize with:

        >>> SearchTypes({
        >>>     'regular': XMLDict,
        >>>     'reverse': ReverseBlahBlah,
        >>> })

        where `custom_types` is just a key-value dict containing a
        string for the  lookup type name, and an uninstantiated class
        derived from XMLDict.
    """

    def add_custom_lookup_type(self, lookup_type, *args, **kwargs):
        """ Register a function for a language ISO to adjust tags used
        in FSTs for use in lexicon lookups. The decorator function takes
        a tuple for every function that the decorator should be applied
        to

        >>> @search_types.add_custom_lookup_type('lookup_type_name')
        >>> class SomeClass(object):
        >>>     pass

        """

        def wrapper(lookup_cls):
            self.search_types[lookup_type] = \
                lookup_cls
            print '%s overrides: custom lookup type - %s' %\
                  ( lookup_type
                  , lookup_cls.__name__
                  )

        return wrapper

    def __init__(self, types):
        self.search_types = types
