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

    def __init__(self, v, table):
        self.header = False
        self.v = v.strip()
        self.table = table
        self.null_value = self.table.options.get('layout', {}).get('no_form', '--')

        if self.v.startswith('"') and self.v.endswith('"'):
            self.header = True

    def __repr__(self):
        return 'V(' + self.v + ')'

    def get_value(self, paradigm):
        if self.header:
            return self.v

        # TODO: get tag splitter from morphology
        v_tags = self.v.split('+')

        for l, tag, forms in paradigm:
            # hackishly join things to check for sublists
            # NB: may need to evaluate regexes here.
            if '###'.join(v_tags) in '###'.join(tag):
                return forms

        return self.null_value

class Null(Value):

    def __init__(self, table):
        self.header = False
        self.v = False
        self.table = table
        self.null_value = self.table.options.get('layout', {}).get('no_form', '--')

    def __repr__(self):
        return 'V(Null)'

    def get_value(self, paradigm):
        return self.null_value

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
    def __init__(self, _str, paradigm=False, options={}):
        self.raw = _str
        self.lines = [a.strip() for a in _str.splitlines() if a.strip()]
        self.paradigm = paradigm

        self.options = options
        self.for_paradigm = self.options.get('paradigm_file', None)

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
                    vals.append(Value(_v, table=self))
                else:
                    vals.append(Null(table=self))
            rows.append(vals)
        return rows

    def fill_generation(self, paradigm):
        """ For a set of generated forms, return a list of lists
            containing generated forms within the parsed structure.

            NB: generated data is in this structure:
                [("lemma", ['Tag1', 'Tag2', 'Tag3'], ['fullform1', 'fullform2']), etc ...]
        """

        as_list = self.to_list()

        rows = []
        for r in as_list:
            row = []
            for c in r:
                cv = c.get_value(paradigm)
                row.append(cv)
            rows.append(row)
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


def get_paradigm(lang, lemma):
    """ Function for testing
    """

    # from neahtta import app

    ps = []


    # with app.app_context():

    #     parads = app.morpholexicon.paradigms
    #     morph = app.config.morphologies.get(lang, False)

    #     lookups = app.morpholexicon.lookup(lemma, source_lang=lang, target_lang='nob')

    #     for node, analyses in lookups:
    #         pp, pt = parads.get_paradigm(lang, node, analyses, return_template=True)
    #         form_tags = [_t.split('+')[1::] for _t in pp.splitlines()]
    #         _generated, _, _ = morph.generate(lemma, form_tags, node, return_raw_data=True)

    #         ps.append(_generated)

    # output from generation
    ps = [[
        (u'mannat', [u'V', u'Ind', u'Prs', u'Sg1'], [u'(mun) manan']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Sg2'], [u'(don) manat']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Sg3'], [u'(son) mann\xe1']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Du1'], [u'(moai) manne']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Du2'], [u'(doai) mannabeahtti']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Du3'], [u'(soai) mannaba']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Pl1'], [u'(mii) mannat']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Pl2'], [u'(dii) mannabehtet']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'Pl3'], [u'(sii) mannet']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Sg1'], [u'mannen']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Sg2'], [u'mannet']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Sg3'], [u'manai']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Du1'], [u'manaime']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Du2'], [u'manaide']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Du3'], [u'manaiga']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Pl1'], [u'manaimet']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Pl2'], [u'manaidet']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'Pl3'], [u'manne']),
        (u'mannat', [u'V', u'Ind', u'Prs', u'ConNeg'], [u'(odne in) mana']),
        (u'mannat', [u'V', u'Ind', u'Prt', u'ConNeg'], [u'(ikte in) mannan']),
        (u'mannat', [u'V', u'PrfPrc'], [u'(lean) mannan'])
    ]]

    return ps

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
            pp, pt = parads.get_paradigm(lang, node, analyses, return_template=True)
            lp, lt = parads.get_paradigm_layout(lang, node, analyses, return_template=True)

            form_tags = [_t.split('+')[1::] for _t in pp.splitlines()]
            _generated, _, _ = morph.generate(lemma, form_tags, node, return_raw_data=True)

            ps.append((lp, _generated))

    return ps

def main():

    fname = sys.argv[1]

    # opts, data = read_layout_file(fname)

    generated_paradigms = get_layout('sme', 'mannat')
    print generated_paradigms

    for layout, paradigm in generated_paradigms:
        print layout.fill_generation(paradigm)


    # print generated_paradigms

    # t = parse_table(data, options=opts)

    # filled_table = t.fill_generation(generated_paradigms[0])



if __name__ == "__main__":
    sys.exit(main())
