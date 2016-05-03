# -*- encoding: utf-8 -*-
"""
Future documentation for wiki:

!!! Paradigm Layouts

Paradigm layouts are defined in a similar way as paradigm generation:
the file structure is one half YAML rules, and the second half defines
the layout. These are split by a line containing only {{{--}}}. As in
the YAML section, spacing is very important, so make sure your text
editor is able to see this. Note also: only use spaces in the layout
definition, tabs may result in errors in processing: confirm that your
text editor will not convert spaces to tabs in any case.

!! An example, and explanation:

TODO: actual working example definition from itwêwina, as well as
screenshots of the result.

    name: "basic"
    layout:
      type: "basic"
    morphology:
      pos: V
      animacy:
        - AI
        - TI
    --
    | "#"  |  "Sg"   |  "Pl"    |
    | "1p" | Prs+1Sg | Prs+1Pl  |
    | "2p" | Prs+2Sg | Prs+12Pl |
    |      |         | Prs+2pl  |
    | "3p" | Prs+3Sg | Prs+3Pl  |
    | "4"  | Prs+4Sg |          |

In the example above, the first half shows that the paradigm is applied
when the morphological analyses for the entry match two tagsets: {{pos}}
and {{animacy}}, where {{pos}} is exactly "V", and {{animacy}} is either
"AI" or "TI". For this to work, these two tagsets must also be defined
in the language project's tagset file. TODO: link to tagset definition.

Some additional information about the layout is also defined, the
{{name}}, and the layout type: layout type is relevant if multiple
layouts are matched for the word and corresponding rule. Multiple
layouts will be rendered in the entry with a tabbed navigation menu at
the top.

Next is the actual layout: here spacing is important, the spacing of all
columns must match up, and columns are marked with the pipe character
{{|}}. It is generally a good idea to leave a space between each pipe
and whatever cell value follows. In addition, the columns for the
beginning and end of the table must be defined, so that each row starts
and begins with {{|}}, otherwise the table may not be parsed correctly.

In order to have a cell span multiple columns, leave out one of the
center pipe characters. (More examples follow).

Cell values may either be a substring of a tag used in generation, or a
string marked in quotes (and some other characters): when the value is
processed, any form with a tag matching this substring will be inserted
into the table, multiple matching values will be split with a line break.

As a cell is defined by one line of text, cell values in the layout
definition may not span multiple lines.

!!! Layout options (YAML)

!! Name, description

Name is mostly used to render the startup log message
as settings are read.

``description`` may be set, in order to display a note to users
underneath the table. This may either be a YAML string, which will be
shown in all languages, or a set of translations:

{{{
description: |
  This is the transitive conjugation, but with no object specified.
}}}

OR

{{{
description:
  eng: |
    This is the transitive conjugation, but with no object specified.
  fra: |
    C'est ne pas une pipe.
}}}

If one translation does not exist, the first language will be used.

!! layout settings

type - (default: unset) - specify the type of the layout and thus its
title in the tab menu if multiple layouts are matched.

**no_form** - default is for the defined value to pass through, if not
generated, i.e., +Whatever+Tag), may specify a space " " for nothing,
note that an empty string ("") will be parsed by YAML as False, so you need a space here.

**value_separator** - default is a line break in html, <br />), other ideas: comma, etc.

**empty_value** - default is nothing, can supply whatever-- note that this is different from **no_form**, which is used only when a form could not be resolved. If certain cells are empty for spacing purposes, define this value here.

!! Morphology and lexicon rules

TODO: paradigm link

!! Referring to rules in other files

Instead of defining a morphology and lexicon rule for matching, you can
use one in another paradigm file. The path may only be relative to the
current language.

{{{
    name: "extended paradigm"
    layout:
      type: "extended"
    paradigm: "some-paradigm-file.paradigm"
}}}


!!! Layout features, and cell values

!! Analysis matches

A successful match of a generated form is represented by a whole tag, or
a substring of the tag.

For the following paradigm, for example:

    foobarbaz foo+V+Prs+Sg1
    foobar    foo+V+Prt+Sg1

A table may be defined:

    | "Present" | +Prs+Sg1 |
    | "Past"    | +Prt+Sg1 |

Or this way:

    | "Present" | V+Prs+Sg1 |
    | "Past"    | V+Prt+Sg1 |

And the HTML table will look thus:

      Present     foobarbaz
      Past        foobar


Alternatively, match all first person forms:

    | "1st P." | +Sg1  |

And the HTML table will look thus:

       1st P.    foobarbaz
                 foobar

Any value that is not matched in the paradigm strings will be passed
through.

!! Constraining the value, match starts with or ends with

Full regular expression matching is not available yet, but two common
features are, the {{^}} and {{$}} characters for anchoring the search
pattern.

TODO: examples from myv
TODO: reconsider: is substring search as a default pattern not
predictable for new linguist users defining a layout?


!! Cell value markings
! Header cells

{{"Text"}}

! Internationalization of string values

{{_"Text"}}

! Cell spanning

Sell spanning is accomplished by leaving out the pipe character.
Currently only spanning horizontally is supported, but not vertically.

{{{

    | "Label" | "Label"   | "Label"         |
    | "Label" | +Some+Tag | +Some+Other+Tag |
    | "Label" |    +Some+Tag                |
    | "Label" | +Some+Tag | +Some+Other+Tag |

}}}

You may either center the text visually, or leave it in the same
position as cells above or below.

NB: this assumes that there is a clearly defined structure to the table,
within the header-- if this is left out the system will not know which
rows are spanning and which rows are empty values.

!! alignment

Aligning text or values within the cell is Value alignment is a matter
of using the character {:} next to the cell border character {|}. Make
sure to also leave a space between this and content inside:

{{{

    |: "Label" | +Tag    :| +Some+Other+Tag |
    |: "Label" |:        +Tag              :|
    |: "Label" | +Tag     | +Some+Other+Tag |

}}}

In most cases you will not need these, because the default style should
automatically center values in spanned cells, and header cells will be
automatically positioned, however you may use alignment to override
this.

!! TODO: value aliases

!!! Programmer notes

TODO: allow definition of match shortcuts

    forms:
      1st_sg:
        - "Prs+1Sg"
        - "Prt+1Sg"
      etc...

    so that match string in table can then be `1st_sg`

So far this is a custom table definition syntax. The YAML section should
be familiar form paradigm definitions: it contains meta information
about the paradigm, as well as a rule which must be satisfied for this
paradigm to be found for a given word lookup and set of morphological
analyses.

Here we are applying this rule to Verbs that are marked as AI or TI as
animacy in the morphological analyses.

The layout section is defined by using the pipe character to define
columns. Quotes are used to mark header rows and columns, so that these
will not be processed when forms are substituted.

Next, the cells containing actual form values must be specified with a
complete or partial tag-- use however much you need, but shorten it if
it helps present it in a concise way.

NOTE: the pipe characters must line up in order for the system to match
all the column values.

If a better table parsing package appears, this should also work as a
drop-in replacement. I am still on the lookout, but evaluated a few and
they didn't initially work out.

--

Ideas:

 * replace the custom parsing / loading of YAML + Jinja with a Jinja
   custom extension so that this processing is included with the normal
   template load process

"""

# NB: formatting ideas here, but no parsers that can be used
# http://www.tablesgenerator.com/markdown_tables or TextTables if
# there's a package for that, supports combined cells-- alternatively
# mediawiki format could be used 


import os, sys
import yaml

class ParadigmException(Exception):

    def __init__(self, template):
        a, _, self.template = template.partition('language_specific_rules')

    def __repr__(self):
        return "%s (in ...%s)" % (self.message, self.template)

    def __unicode__(self):
        return "%s (in ...%s)" % (self.message, self.template)

    def __str__(self):
        return "%s (in ...%s)" % (self.message, self.template)

class ParadigmParseError(ParadigmException):
    message = "Table definition appears to be blank"

class NoTableDefinition(ParadigmParseError):
    message = "Table is missing a header"

class UnevenRowLengths(ParadigmParseError):
    message = "Row lengths are uneven, could not parse."

class Value(object):
    """ The cell Value, which is calculated by the current paradigm and
        Cell object.
    """

    VALUE_SEPARATOR = ', '

    def set_options(self):
        layout_opts = self.table.options.get('layout', {})

        self.null_value = layout_opts.get('no_form', False)
        self.VALUE_SEPARATOR = layout_opts.get('value_separator', '<br />')
        self.search_type = layout_opts.get('form_search_type', False)

    def __init__(self, cell, table, paradigm):
        self.cell = cell
        self.table = table
        self.paradigm = paradigm

        self.set_options()
        self.value = self.get_value()

    def compare_value(self, tag_list):
        """ Returns true or false depending on whether a and b are a
        match

        TODO: enable full regex option?

        for now only supporting 'fake' regex, e.g., typical startswith
        endswith characters

        TODO: multiple matches?

        """

        def tag_splitter(x):
            splitted = self.paradigm[0].tool.splitAnalysis(x)
            return [a for a in splitted if a]

        search_tags = tag_splitter(self.cell.v)

        search_predicate = '###'.join(search_tags)
        current_form_tag = '###'.join(tag_list)

        if self.cell.v.endswith('$') and not self.cell.v.endswith('\$'):
            search_tags = tag_splitter(self.cell.v[0:-1])
            search_predicate = '###'.join(search_tags)

            return current_form_tag.endswith(search_predicate)

        if self.cell.v.startswith('^'):
            search_tags = tag_splitter(self.cell.v[1::])
            search_predicate = '###'.join(search_tags)

            return current_form_tag.startswith(search_predicate)

        # Otherwise case is a substring match
        return search_predicate in current_form_tag

    def fill_value(self):

        values_list = []
        for generated_form in self.paradigm:
            tag = generated_form.tag.parts
            if self.compare_value(tag):
                print tag
                print generated_form.form
                self.value_type = list
                values_list.append(generated_form.form)

        return values_list

    def get_value(self):
        # Check to see if cell is any other type than a computed value
        if self.cell.header:
            self.value_type = self.cell
            return self.cell.v

        if not self.cell.v:
            self.value_type = self.cell
            return self.cell.empty_cell

        # Compute the value ... 
        values_list = self.fill_value()

        if len(values_list) > 0:
            return self.VALUE_SEPARATOR.join(values_list)
        else:
            # TODO: null cell value vs. blank value in parsing
            # definition
            if self.null_value:
                return self.null_value
            else:
                return self.cell.v

        self.value_type = self.cell
        return self.cell

    # TODO: implies a problem here, return type of get_value should be
    # useful
    def __repr__(self):
        if type(self.value_type) in [Cell, Null]:
            return 'Value(' + repr(self.value) + ')'
        else:
            return 'Value(' + repr(self.value) + ')'

class Cell(object):
    """ A table Cell, includes parser method for determining how a Value
        should be looked up.

        TODO: does markdown on a single string slow things down? Could
        use that for additional style features.
    """

    def __init__(self, v, table, index):
        self.index = index
        self.col_span = False
        self.header = False
        self.internationalize = False
        self.v = v.strip()
        self.table = table
        self.null_value = self.table.options.get('layout', {}).get('no_form', '')
        self.empty_cell = self.table.options.get('layout', {}).get('empty_cell', '')
        self.text_align = False

        self.clean_value()

    def update_value(self, new_value):
        self.v = new_value
        self.clean_value()

    def clean_value(self):
        # strip off alignment marks, and then continue to process
        if self.v.startswith(':') and self.v.endswith(':'):
            self.v = self.v[1:-1].strip()
            self.text_align = 'center'
        elif self.v.startswith(':'):
            self.v = self.v[1::].strip()
            self.text_align = 'left'
        elif self.v.endswith(':'):
            self.v = self.v[0:-1].strip()
            self.text_align = 'right'

        if self.v.startswith('_"') and self.v.endswith('"'):
            self.header = True
            self.v = self.v[2:len(self.v)-1]
            self.internationalize = True

        if self.v.startswith('"') and self.v.endswith('"'):
            self.header = True
            self.v = self.v[1:len(self.v)-1]

    def __repr__(self):
        return 'Cell(' + self.v + ')'

class Null(Cell):

    def __init__(self, table, index):
        self.index = index
        self.header = False
        self.v = False
        self.table = table
        self.no_form = self.table.options.get('layout', {}).get('no_form', '')
        self.empty_cell = self.table.options.get('layout', {}).get('empty_cell', '')

    def __repr__(self):
        return 'V(Null)'

    def get_value(self, paradigm):
        return self.empty_cell

class FilledParadigmTable(object):
    """ Convenience object for the template stuff. This is probably the
    ``layout`` or ``l`` objects in templates.
    """

    def __init__(self, paradigm_table, as_list):
        self.table = paradigm_table.table
        self.rows = []

        for r in as_list:
            row = []
            for c in r:
                v = Value(c, self.table, paradigm_table.paradigm)
                row.append(v)
            self.rows.append(row)

    def get_description(self, *langs):

        descs = self.table.options.get('description', False)
        print descs
        print langs

        # User has defined multiple languages, so we pick one from the
        # args in order, and if that doesn't exist return the first
        if isinstance(descs, dict):
            if len(langs) > 0:
                for l in langs:
                    if l in descs:
                        return descs.get(l)
            return descs.values()[0]
        # It's just a string
        else:
            return descs


class ParadigmTable(object):
    """ An instance of a Table prepared for a particular word's
        inflectional paradigm. Avoids a Table being reused and
        potentially filled with old values.
    """

    def __init__(self, table, paradigm):
        self.table = table
        self.paradigm = paradigm

    def fill_generation(self):
        """ For a set of generated forms, return a list of lists
            containing generated forms within the parsed structure.

            NB: generated data is in this structure:
                [("lemma", ['Tag1', 'Tag2', 'Tag3'], ['fullform1', 'fullform2']), etc ...]
        """

        as_list = self.table.to_list()

        return FilledParadigmTable(paradigm_table=self, as_list=self.table.to_list())

class TableParser(object):
    """ Methods for parsing the tables
    """

    COLUMN_DELIM = '|'

    # NB: after evaluating tons of parsers for this exact type of
    # thing, found that none of them seemed reasonable. If a good one
    # exists, it should be possible to replace with some of this code
    # here.

    @property
    def header_positions(self):
        """ Return list of integers for header positions """

        # TODO: this will break if the first line has a spanned cell
        # that does not exist in other rows: possible to check all rows
        # and then determine which is most common split?

        if hasattr(self, '_header_positions'):
            return self._header_positions

        # Generator for indexes of column delimiter characters
        heads = (i for i, c in enumerate(self.header)
                   if c == self.COLUMN_DELIM)

        self._header_positions = list(heads)
        return self._header_positions

    @property
    def column_positions(self):
        """ Return a list of tuples of the column bounds """

        if hasattr(self, '_column_positions'):
            return self._column_positions

        _pos = []

        first, last = False, False
        for a in self.header_positions:
            if not first:
                first = True
                last = a
                continue
            _pos.append((last, a))
            last = a

        self._column_positions = _pos
        return self._column_positions

    @property
    def header(self):
        """ The header line
        """
        return self.lines[0]

    @property
    def lines(self):
        """ The lines of the table string.
        """
        if hasattr(self, '_lines'):
            return self._lines

        # Clean whitespace and split lines
        ls = [a.strip() for a in self.raw.splitlines()]

        # Remove null lines
        self._lines = [l for l in ls if l]

        return self._lines

    # TODO: paradigm
    def __init__(self, _str, options={}):
        self.raw = _str
        self.options = options

    def validate(self):
        errors = {}
        success = True

        try:
            b = self.header
        except Exception, e:
            errors['header'] = NoTableDefinition(self.options['META'].get('path'))
            success = False

        if len(self.lines) == 0:
            errors['table'] = NoTableDefinition(self.options['META'].get('path'))
            success = False
        else:
            lengths = set()
            for l in self.lines:
                lengths.add(len(l))

            if len(lengths) != 1:
                errors['rows'] = UnevenRowLengths(self.options['META'].get('path'))
                success = False

        print self.to_list()

        return (success, errors)

    def to_list(self):
        """ Create a list of rows, containing Cell or Null objects.
        """

        # TODO: possibly detect merged cells? if delimiter doesn't exist
        # at expected point, merge

        cs = self.column_positions

        rows = []
        cell_count = 0

        for row in self.lines:
            vals = []
            merge = 0
            last_cell = None
            extend_value = False

            for (a, b) in cs:

                _v = row[a+1:b]

                end_span = row[a] != self.COLUMN_DELIM
                begin_span = row[b] != self.COLUMN_DELIM
                # > 2 column spans
                continue_span = begin_span and end_span

                # There is no delimiter so, the cells need to be merged,
                # which will be merge > 0, will then use this as the
                # colspan.
                if begin_span or continue_span or end_span:
                    merge += 1
                else:
                    merge = 0
                # mark the beginning of the value
                if begin_span:
                    extend_value = a+1

                # If we're in the middle of a span, do nothing and
                # continue
                if continue_span:
                    continue
                # At the end of the span, update the value with where
                # the span began, and set the colspan of the span's cell
                # And then reset the merge values.
                elif end_span:
                    _v = row[extend_value:b-1]
                    last_cell.col_span = merge
                    last_cell.update_value(_v.strip())
                    merge = 0
                    last_cell = None
                    extend_value = False
                # Otherwise, no span, so do the normal thing and also
                # set the last cell and increment
                else:
                    if len(_v.strip()) > 0:
                        last_cell = Cell(_v, table=self, index=cell_count)
                    else:
                        last_cell = Null(table=self, index=cell_count)
                    vals.append(last_cell)
                    cell_count += 1

            rows.append(vals)
        print rows
        return rows


class Table(TableParser):
    """ The paradigm table parser and parsed table representation,
        including options.

        >>> table = Table(table_string, options)

    """

    def for_paradigm(self, paradigm):
        """ With a generated list of GeneratedForm objects (`paradigm`),
            create a ParadigmTable instance

            >>> instance = table.for_paradigm(paradigm)

            Then fill in the generation from the paradigm, and return a
            list of rows containing cells.

            >>> rendered_layout = instance.fill_generation()
        """

        return ParadigmTable(self, paradigm)

def parse_table(table_string, yaml_definition, path=False):
    """ Parse the ASCII table, with options, return a Table object.
    """
    yaml_definition['META'] = {
        'path': path
    }
    t = Table(table_string, options=yaml_definition)

    valid, errors = t.validate()

    if valid:
        return (t, {})
    else:
        return (False, errors)
