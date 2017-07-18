""" Filter the results of an XPath query through a command.

Usage: tools/filter_xpath.py <xpath_node> <xpath_statement> <commandline_tool>

Options:
    -h --help                  Show this screen.
    -v --verbose               Verbose.
    -e --encoding-format=FMT   Encoding format. [default: m4a]
    -l --local-audio-source    Use local file source, do not download [default: false]
    -o --output-file=PATH      Destination file for edited XML
"""

# TODO: option for no fetch, incase they are stored locally: <path_to_audio> is
# the target compressed audio store for now, but could serve as local copy too
# 
# python tools/extract_audio.py dicts/sms-all.xml static/aud/sms --verbose > test_aud.xml


# TODO: only download updated files, storing in manifest in path/to/stored/audio/
from docopt import docopt

import os, sys
import requests

from lxml import etree

command = None
from sh import hfst_lookup

def run_cmd(_in):
    tool = hfst_lookup('/Users/pyry/gtsvn/langs/crk/src/orthography/Latn-to-Cans.lookup.hfst', _in=_in.encode('utf-8'), _bg=True)
    stsrs = []
    for l in tool.split('\n\n'):
        ll = l.split('\t')
        if len(ll) == 3:
            stsrs.append(ll[1])
        else:
            stsrs.append('--')
    return stsrs

# lxml_root, [(source, target), ... ]
def replace_xpath(xml_root, nodes, elems):
    import copy
    root_duplicate = copy.deepcopy(xml_root)

    all_nodes = etree.XPath(
        nodes,
    )(root_duplicate)

    # nodes with audios get replaced with the new URL.
    print >> sys.stderr,  len(all_nodes)
    n = 0
    convert = []
    for node in all_nodes:
        strs = node.xpath(elems)
        convert.append(strs[0].text)

    print >> sys.stderr, len(convert)
    converted = run_cmd('\n'.join(convert))
    print >> sys.stderr, len(converted)
    for c, node in zip(converted, all_nodes):
        strs = node.xpath(elems)
        # print c, strs[0].text
        strs[0].text = c.strip()
    # new xml root
    return root_duplicate

def write_xml(root, output_file=False):
    # TODO: strips some headers
    stringed = etree.tostring(root, pretty_print=True, method='xml',
                              encoding='unicode')

    if output_file is not None:
        with open(output_file, 'w') as F:
            F.write(stringed.encode('utf-8'))
    else:
        print >> sys.stdout, stringed.encode('utf-8')

# def init_tool(path):
#     from sh import hfst_lookup
#     tool = hfst_lookup('/Users/pyry/gtsvn/langs/crk/src/orthography/Latn-to-Cans.lookup.hfst', _in="nipi", _bg=True)
#     return tool

def main():

    arguments = docopt(__doc__, version='asdf')

    # Usage: tools/filter_xpath.py <xpath_node> <xpath_statement> <commandline_tool>

    xp_n = arguments.get('<xpath_node>')
    xp = arguments.get('<xpath_statement>')
    # tool = init_tool(arguments.get('<commandline_tool>'))

    root = etree.parse(sys.stdin)

    updated_xml = replace_xpath(root, nodes=xp_n, elems=xp)
    write_xml(updated_xml, arguments.get('--output-file'))
    return 0

if __name__ == "__main__":
    sys.exit(main())

