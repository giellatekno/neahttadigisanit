# -*- encoding: utf-8 -*-
"""
Future documentation for wiki:

! Internationalization of string values

{{_"Text"}}

!!! Programmer notes

TODO: FEATURE - hover over labels for tooltip that explains them
    - need mobile solution too, maybe there it should be click not hover

TODO: FEATURE - cells need multiple tags, etc

TODO: BUG - key help not present on detail views

TODO: possible to convert a table into a plain list for mobile devices

TODO: tagsets vs. internationalization files?
    - perhaps easiest to leave all paradigm translation of strings
    to tagsets for now, otherwise will have to develop a parser for
    babel that can extract these, or use a yaml setting in the
    header to provide strings for these, e.g.:

        extra_translations:
          fin:
            "Plural": "monikko"
        --
        | _"Plural" | etc  |
        | bbq       | foo  |

TODO: multiple cell values, e.g., _"Sg" _"Prs"
      or for context, e.g., "(mun)" Ind+Prs+1Sg

      will need to redo cell value parser

down the line ...

todo: value aliases?
todo: allow definition of match shortcuts

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
        layout_opts = DEFAULT_OPTIONS.copy().get('layout')
        layout_opts.update(**self.table.options.get('layout', {}))

        self.null_value = layout_opts.get('no_form')
        self.VALUE_SEPARATOR = layout_opts.get('value_separator')

    def __init__(self, cell, table, paradigm):
        self.cell = cell
        self.table = table
        self.paradigm = paradigm

        self.set_options()
        self.value = self.get_value()

    def compare_value(self, tag_list, lemma):
        """ Returns true or false depending on whether a and b are a
        match

        possibilities:
            - ^Tag+Omg+Bbq
            - Tag+Omg+Bbq$
            - ^Tag+Omg+Bbq$
            - =Tag+Omg+Bbq

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

        search_v = self.cell.v

        if '{{ lemma }}' in search_v:
            search_v = search_v.replace('{{ lemma }}', lemma)
            # search_predicate = '###'.join(search_v)

        if 'LEMMA' in search_v:
            search_v = search_v.replace('LEMMA', lemma)
            # search_predicate = '###'.join(search_v)

        if search_v.startswith('^') and search_v.endswith('$'):
            search_tags = tag_splitter(search_v[1:-1])
            search_predicate = '###'.join(search_tags)
            return current_form_tag == search_predicate

        if search_v.endswith('$') and not search_v.endswith('\$'):
            search_tags = tag_splitter(search_v[0:-1])
            search_predicate = '###'.join(search_tags)

            return current_form_tag.endswith(search_predicate)

        if search_v.startswith('^'):
            search_tags = tag_splitter(search_v[1::])
            search_predicate = '###'.join(search_tags)

            return current_form_tag.startswith(search_predicate)

        if search_v.startswith('='):
            search_tags = tag_splitter(search_v[1::])
            search_predicate = '###'.join(search_tags)
            return current_form_tag == search_predicate

        if '*' in search_v:
            start_search, _, end_search = search_v.partition('*')
            start_search_tags = tag_splitter(start_search)
            end_search_tags = tag_splitter(end_search)
            start_search_pred = '###'.join(start_search_tags)
            end_search_pred = '###'.join(end_search_tags)
            return current_form_tag.startswith(start_search_pred) and \
                   current_form_tag.endswith(end_search_pred)


        # Otherwise case is a substring match
        return search_predicate in current_form_tag

    def fill_value(self):
        # NB: see #multi_value

        values_list = []
        for generated_form in self.paradigm:
            tag = generated_form.tag.parts
            if self.compare_value(tag, generated_form.lemma):
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
        # TODO: if multiple values in a cell are to be allowed, e.g.
        #  | _"1Sg" _"Prs" |, need to improve the parsing here
        # to be an actual parser, this should return a list of tokens or
        # something, and then see #multi_value for where this will be
        # handled


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

        if list(set(self.v)) == ['-']:
            self.horizontal_line = True
            self.v = ''

    def __repr__(self):
        return 'Cell(' + self.v + ')'

class Null(Cell):

    def __init__(self, table, index):
        self.index = index
        self.header = False
        self.horizontal_line = False
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

DEFAULT_OPTIONS = {
    'layout': {
        'type': "basic",
        'no_form': False,
        'value_separator': '<br />',
    },
}

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
    def __init__(self, _str, options=False):
        self.raw = _str
        opts = DEFAULT_OPTIONS.copy()
        if options:
            opts.update(**options)
        self.options = opts

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
