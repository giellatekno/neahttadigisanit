# -*- encoding: utf-8 -*-
"""
Future documentation for wiki:

!!! Paradigm Layouts

You may also define a paradigm layout to go with the paradigm files. A quick example definition first:

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


TODO: settings on the row for when it has no generated values

TODO: what to display when the table layout asks for a value that is not
      present?

TODO: default paradigm type in options

TODO: Alternatively the user should be able to specify a .paradigm file
      to grab the morphology and lexicon rules.

TODO: allow definition of match shortcuts

    forms:
      1st_sg:
        - "Prs+1Sg"
        - "Prt+1Sg"
      etc...

    so that match string in table can then be `1st_sg`

TODO: allow internationalization on header values

    _"Sg"

TODO: combined cells

So far this is a custom table definition syntax. The YAML section should
be familiar form paradigm definitions: it contains meta information
about the paradigm, as well as a rule which must be satisfied for this
paradigm to be found for a given word lookup and set of morphological
analyses.

Here we are applying this rule to Verbs that are marked as AI or TI as
aniacy in the morphological analyses.

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

# Main TODOs:
# TODO: Need to produce a config object very similar to ParadigmConfig that
# can instead select the proper table for a paradigm, and then also
# produce the rendered table.

# TODO: if a paradigm can't be found, fall back to existing NDS
# rendering process, and if something breaks, make sure that we can fall
# back to this then too.

# TODO: markdown tables any better?
# http://www.tablesgenerator.com/markdown_tables or TextTables if
# there's a package for that, supports combined cells-- alternatively
# mediawiki format could be used 


import os, sys
import yaml

class Value(object):
    """ The cell Value, which is calculated by the current paradigm and
        Cell object.
    """

    VALUE_SEPARATOR = ', '

    def __init__(self, cell, table, paradigm):
        self.cell = cell
        self.table = table
        self.paradigm = paradigm
        self.null_value = self.table.options.get('layout', {}).get('no_form', '')
        self.VALUE_SEPARATOR = self.table.options.get('layout', {}).get('value_separator', '<br />')

        self.value = self.get_value()

    def get_value(self):
        if self.cell.header:
            self.value_type = self.cell
            return self.cell.v

        if not self.cell.v:
            self.value_type = self.cell
            return self.cell.null_value

        values_list = []
        for generated_form in self.paradigm:
            tag = generated_form.tag.parts
            v_tags = generated_form.tool.splitAnalysis(self.cell.v)

            # hackishly join things to check for sublists
            # NB: may need to evaluate regexes here.
            if '###'.join(v_tags) in '###'.join(tag):
                self.value_type = list
                values_list.append(generated_form.form)

        if len(values_list) > 0:
            return self.VALUE_SEPARATOR.join(values_list)

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

        if self.v.startswith('~"') and self.v.endswith('"'):
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
        self.null_value = self.table.options.get('layout', {}).get('no_form', '')

    def __repr__(self):
        return 'V(Null)'

    def get_value(self, paradigm):
        return self.null_value

class FilledParadigmTable(object):
    """ Convenience object for the template stuff.
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

    def to_list(self):
        """ Create a list of rows, containing Cell or Null objects.
        """

        # TODO: possibly detect merged cells? if delimiter doesn't exist
        # at expected point, merge

        cs = self.column_positions

        rows = []
        cell_count = 0
        print 'begin'
        for row in self.lines:
            vals = []
            merge = 0
            last_cell = None
            extend_value = False

            for (a, b) in cs:
                print cell_count

                _v = row[a+1:b-1]

                end_span = row[a] != self.COLUMN_DELIM
                begin_span = row[b] != self.COLUMN_DELIM
                # > 2 column spans
                continue_span = begin_span and end_span
                print _v
                print begin_span, continue_span, end_span

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
                    last_cell.v = _v.strip()
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
        print 'end'
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

def parse_table(table_string, yaml_definition):
    """ Parse the ASCII table, with options, return a Table object.
    """
    t = Table(table_string, options=yaml_definition)
    return t
