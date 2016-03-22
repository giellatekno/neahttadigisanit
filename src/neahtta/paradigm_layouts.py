# -*- encoding: utf-8 -*-
"""
layout:
  type: "basic"
paradigm_file: 'verbs-ai-ti.paradigm'
--
|  #   |  "Sg"   |  "Pl"    |
| "1p" | Prs+1Sg | Prs+1Pl  |
| "2p" | Prs+2Sg | Prs+12Pl |
|      |         | Prs+2pl  |
| "3p" | Prs+3Sg | Prs+3Pl  |
| "4"  | Prs+4Sg |          |


"""


import os, sys
import yaml

class Value(object):

    # TODO: Compute the value based on paradigms or something

    def __init__(self, v, table):
        self.header = False
        self.v = v.strip()
        self.table = table
        self.null_value = '--'

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
        self.null_value = '--'

    def __repr__(self):
        return 'V(Null)'

    def get_value(self, paradigm):
        return self.null_value

class Table(object):

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
    def __init__(self, _str, paradigm=False):
        self.raw = _str
        self.lines = [a.strip() for a in _str.splitlines() if a.strip()]
        self.paradigm = paradigm

    # def data_rows(self):

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

def parse_table(table_string):
    t = Table(table_string)
    return t

def read_layout_file(fname):
    import yaml

    with open(fname, 'r') as F:
        data = F.read()

    opts, _, data = data.partition('--')

    options = yaml.load(opts)

    return (options, data)


# just for testing
def get_paradigm(lang, lemma):
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

def main():


    fname = sys.argv[1]

    opts, data = read_layout_file(fname)

    generated_paradigms = get_paradigm('sme', 'mannat')
    # print generated_paradigms

    t = parse_table(data)

    filled_table = t.fill_generation(generated_paradigms[0])

    print filled_table


if __name__ == "__main__":
    sys.exit(main())
