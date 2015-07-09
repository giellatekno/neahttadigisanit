# -*- encoding: utf-8 -*-
import os, sys

pre_lemma_tags = [
    'RdplW',
    'RdplS',
]

# TODO: replace PV/ with user-defined regex or something
def process_crk_analysis(analysis_line):
    """ Take an analysis line, and return a tuple of the lemma,
    followed by a reformatted tag where tags before the lemma are
    combined with tags after the lemma. Strings without any preverb
    material are not changed.

        >>> process_crk_analysis("wordform\tPV/asdf+PV/bbq+lemma+POS+Type+Sg1")
        ('wordform', 'lemma+PV/asdf+PV/bbq+POS+Type+Sg1')
        >>> process_crk_analysis("wordform\tlemma+POS+Type+Sg1")
        ('wordform', 'lemma+POS+Type+Sg1')
        >>> process_crk_analysis("wordform\tPV/asdf+PV/bbq+lemma")
        ('wordform', 'lemma+PV/asdf+PV/bbq')
        >>> process_crk_analysis("ninahnipan\tRdplS+nipâw+V+AI+Ind+Prs+1Sg")
        ('ninahnipan', 'nipâw+RdplS+V+AI+Ind+Prs+1Sg')
        >>> process_crk_analysis("ninanahnipan\tRdplW+RdplS+nipâw+V+AI+Ind+Prs+1Sg")
        ('ninanahnipan', 'nipâw+RdplW+RdplS+V+AI+Ind+Prs+1Sg')
    """

    wordform, _, analysis_string = analysis_line.partition('\t')

    lemma = False

    tag_sep = '+'

    parts = analysis_string.split(tag_sep)
    has_preverbs = False

    for p in parts:
        if p.startswith('PV/') or p in pre_lemma_tags:
            has_preverbs = True
        else:
            lemma = p
            break

    preverbs, _, tag = analysis_string.partition(tag_sep + lemma + tag_sep)

    # When there is no `tag` from the partition ...
    if len(tag) == 0:
        # ... because there are preverbs and nothing else
        if has_preverbs:
            # remove the lemma from the tag
            preverbs = preverbs.replace(tag_sep + lemma, '')
        # ... because there are no preverbs
        else:
            _lem, _, tag = analysis_string.partition(lemma + tag_sep)
            preverbs = None

    reformatted_tag_parts = [lemma]

    if preverbs:
        reformatted_tag_parts.append(preverbs)
    if tag:
        reformatted_tag_parts.append(tag)

    reformatted_tag = tag_sep.join(reformatted_tag_parts)

    return (wordform, reformatted_tag)

def main():
    print '--'
    print process_crk_analysis("PV/asdf+PV/bbq+lemma+POS+Type+Sg1")
    # ('lemma', 'PV/asdf+PV/bbq+POS+Type+Sg1')
    print process_crk_analysis("lemma+POS+Type+Sg1")
    # ('lemma', 'lemma+POS+Type+Sg1')
    print process_crk_analysis("PV/asdf+PV/bbq+lemma")

    print process_crk_analysis("ninahnipan\tRdplS+nipâw+V+AI+Ind+Prs+1Sg")
    # ('ninahnipan', 'nipâw+RdplS+V+AI+Ind+Prs+1Sg')
    print process_crk_analysis("ninanahnipan\tRdplW+RdplS+nipâw+V+AI+Ind+Prs+1Sg")
    # ('ninanahnipan', 'nipâw+RdplW+RdplS+V+AI+Ind+Prs+1Sg')

if __name__ == "__main__":
    sys.exit(main())

