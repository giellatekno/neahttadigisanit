""" Filter the results of an XPath query through a command.

Usage: tools/filter_pofile.py <in_path> <out_path>

Options:
    -h --help                  Show this screen.
    -v --verbose               Verbose.
"""

# TODO: option for no fetch, incase they are stored locally: <path_to_audio> is
# the target compressed audio store for now, but could serve as local copy too
#
# python tools/extract_audio.py dicts/sms-all.xml static/aud/sms --verbose > test_aud.xml

import os
import sys

from lxml import etree

# TODO: only download updated files, storing in manifest in path/to/stored/audio/
from docopt import docopt
from sh import hfst_lookup

command = None


def run_cmd(_in):
    l = hfst_lookup(
        '/Users/pyry/gtsvn/langs/crk/src/orthography/Latn-to-Cans.lookup.hfst',
        _in=_in.encode('utf-8'),
        _bg=True)
    stsrs = []
    ll = l.split('\t')
    if len(ll) == 3:
        return ll[1]
    else:
        return False


def write_pofile(root, output_file=False):
    # TODO: strips some headers
    stringed = etree.tostring(
        root, pretty_print=True, method='xml', encoding='unicode')

    if output_file is not None:
        with open(output_file, 'w') as F:
            F.write(stringed.encode('utf-8'))
    else:
        print >> sys.stdout, stringed.encode('utf-8')


def fetch_messages(path):
    from polib import pofile

    _pofile = pofile(path)

    for e in _pofile:
        if e.msgstr:
            x = run_cmd(e.msgstr)
            if e.msgstr != x:
                print e.msgstr, x
                e.msgstr = x
    # TODO: rewrite

    return _pofile


def main():

    arguments = docopt(__doc__, version='asdf')

    # Usage: tools/filter_xpath.py <xpath_node> <xpath_statement> <commandline_tool>

    print arguments
    in_f = arguments.get('<in_path>')
    out_f = arguments.get('<out_path>')

    print in_f
    ms = fetch_messages(in_f)
    ms.save(fpath=out_f)

    # updated_xml = replace_xpath(root, nodes=xp_n, elems=xp)
    # write_xml(updated_xml, arguments.get('--output-file'))
    return 0


if __name__ == "__main__":
    sys.exit(main())
