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

TODO: Alternatively the user should be able to specify a .paradigm file
      to grab the morphology and lexicon rules.

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

# TODO: make this a module


import os, sys
import yaml

class Value(object):

    def __init__(self, cell, table, paradigm):
        self.cell = cell
        self.table = table
        self.paradigm = paradigm
        self.value = self.get_value()

    def get_value(self):
        if self.cell.header:
            self.value_type = self.cell
            return self.cell.v

        for generated_form in self.paradigm:
            # l, tag, forms 
            tag = generated_form.tag.parts
            v_tags = generated_form.tool.splitAnalysis(self.cell.v)
            # hackishly join things to check for sublists
            # NB: may need to evaluate regexes here.
            if '###'.join(v_tags) in '###'.join(tag):
                self.value_type = list
                return generated_form.form

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

    def __init__(self, v, table):
        self.header = False
        self.v = v.strip()
        self.table = table
        self.null_value = self.table.options.get('layout', {}).get('no_form', '--')

        if self.v.startswith('"') and self.v.endswith('"'):
            self.header = True

    def __repr__(self):
        return 'Cell(' + self.v + ')'

class Null(Cell):

    def __init__(self, table):
        self.header = False
        self.v = False
        self.table = table
        self.null_value = self.table.options.get('layout', {}).get('no_form', '--')

    def __repr__(self):
        return 'V(Null)'

    def get_value(self, paradigm):
        return self.null_value

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

        rows = []
        for r in as_list:
            row = []
            for c in r:
                # cv = c.get_value(self.paradigm)
                v = Value(c, self.table, self.paradigm)
                row.append(v)
            rows.append(row)
        return rows

class Table(object):

    # TODO: after evaluating tons of parsers for this exact type of
    # thing, found that none of them seemed reasonable. If a good one
    # exists, it should be possible to replace with some of this code
    # here.

    @property
    def header_positions(self):
        """ Return list of integers for header positions """
        return list( (i for i, x in enumerate(self.header) if x == '|') )

    @property
    def column_positions(self):
        """ Return a list of tuples of the column bounds """
        pos = []
        first = False
        last = False
        for a in self.header_positions:
            if not first:
                first = True
                last = a
                continue
            pos.append((last, a))
            last = a

        return pos

    @property
    def header(self):
        return self.lines[0]

    # TODO: paradigm
    def __init__(self, _str, options={}):
        self.raw = _str
        self.lines = [a.strip() for a in _str.splitlines() if a.strip()]
        # self.paradigm = paradigm

        self.options = options
        # self.for_paradigm = self.options.get('paradigm_file', None)

    def for_paradigm(self, paradigm):
        return ParadigmTable(self, paradigm)

    def to_list(self):
        # TODO: possibly detect merged cells? if delimiter doesn't exist
        # at expected point, merge

        cs = self.column_positions

        rows = []
        for row in self.lines:
            vals = []
            for (a, b) in cs:
                _v = row[a+1:b-1]
                if _v.strip():
                    vals.append(Cell(_v, table=self))
                else:
                    vals.append(Null(table=self))
            rows.append(vals)
        return rows

def parse_table(table_string, options):
    t = Table(table_string, options=options)
    return t

def read_layout_file(fname):
    import yaml

    with open(fname, 'r') as F:
        data = F.read()

    opts, _, data = data.partition('--')

    options = yaml.load(opts)

    return (options, data)


def get_layout(lang, lemma):
    """ A test function for developing this, return (parsed_layout, generated_paradigm)
    """
    from neahtta import app

    ps = []
    with app.app_context():

        parads = app.morpholexicon.paradigms
        morph = app.config.morphologies.get(lang, False)

        lookups = app.morpholexicon.lookup(lemma, source_lang=lang, target_lang='nob')

        for node, analyses in lookups:
            if (node is not None) and analyses:
                pp, pt = parads.get_paradigm(lang, node, analyses, return_template=True)
                lp, lt = parads.get_paradigm_layout(lang, node, analyses, return_template=True)

                form_tags = [_t.split('+')[1::] for _t in pp.splitlines()]
                _generated, _, _ = morph.generate_to_objs(lemma, form_tags, node, return_raw_data=True)

                ps.append((lp, _generated))

    return ps

def main():

    fname = sys.argv[1]

    # opts, data = read_layout_file(fname)

    generated_paradigms = get_layout('sme', 'vuovdit')
    # print generated_paradigms

    for layout, paradigm in generated_paradigms:
        if layout:
            rows = layout.for_paradigm(paradigm).fill_generation()
            for r in rows:
                for value in r:
                    if value.cell.header:
                        print '**' + value.value + '**'
                    else:
                        print ', '.join(value.value)

        else:
            print "no layout found"

    # print generated_paradigms

    # t = parse_table(data, options=opts)

    # filled_table = t.fill_generation(generated_paradigms[0])



if __name__ == "__main__":
    sys.exit(main())
