def remove_blank(generated_result, *generation_input_args):
    """ **Remove empty analyses**

    This is a language specific filter, more or less to aid in discovery
    of analyser errors with new language sets.
    """
    def _strip((lemma, tag_list, analyses)):
        if not analyses:
            return False
        return True

    return filter(_strip, generated_result)

def match_homonymy_entries(entries_and_tags):
    """ **Post morpho-lexicon override**

    This is performed after lookup has occurred, in order to filter out
    entries and analyses, when these depend on eachother.

    Here: we only want to return entries where the analysis homonymy tag
    matches the entry homonymy attribute. If entries do not have a
    homonymy attribute, then always return the entry.
    """

    filtered_results = []

    for entry, analyses in entries_and_tags:
        if entry is not None:
            entry_hid = entry.find('lg/l').attrib.get('hid', False)
            if entry_hid:
                # Sometimes tags don't have hid, but entry does. Thus:
                tag_hids = [x for x in [a.tag['homonyms'] for a in analyses]
                            if x is not None]
                if len(tag_hids) > 0:
                    # if they do, we do this
                    if entry_hid in tag_hids:
                        filtered_results.append((entry, analyses))
                else:
                    filtered_results.append((entry, analyses))
            else:
                filtered_results.append((entry, analyses))
        else:
            filtered_results.append((entry, analyses))

    return filtered_results
