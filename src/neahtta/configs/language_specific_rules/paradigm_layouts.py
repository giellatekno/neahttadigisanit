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

# import asciitable
# from asciitable import FixedWidth

class Value(object):

    def __init__(self, v):
        self.header = False

        self.v = v.strip()

        if self.v.startswith('"') and self.v.endswith('"'):
            self.header = True

    def __repr__(self):
        return 'V(' + self.v + ')'

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

    def __init__(self, _str):
        self.raw = _str
        self.lines = [a.strip() for a in _str.splitlines() if a.strip()]

    # def data_rows(self):

    def to_list(self):
        # TODO: possibly detect merged cells? if delimiter doesn't exist
        # at expected point, merge

        cs = self.column_positions

        rows = []
        for row in self.lines:
            vals = []
            for (a, b) in cs:
                vals.append(Value(row[a+1:b-1]))
            rows.append(vals)
        return rows

def parse_table(table_string):
    t = Table(table_string)
    print t.to_list()
    return t.to_list()

def read_layout_file(fname):
    import yaml

    with open(fname, 'r') as F:
        data = F.read()

    opts, _, data = data.partition('--')

    options = yaml.load(opts)

    return (options, data)

def main():
    fname = sys.argv[1]

    opts, data = read_layout_file(fname)

    print parse_table(data)

if __name__ == "__main__":
    sys.exit(main())
