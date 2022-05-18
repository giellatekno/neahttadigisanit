def remove_blank(generated_result, *generation_input_args, **kwargs):
    """ **Remove empty analyses**

    This is a language specific filter, more or less to aid in discovery
    of analyser errors with new language sets.
    """

    def _strip(xxx_todo_changeme):
        (lemma, tag_list, analyses) = xxx_todo_changeme
        if not analyses:
            return False
        return True

    return list(filter(_strip, generated_result))


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
                tag_hids = [
                    x for x in [a.tag['homonyms'] for a in analyses]
                    if x is not None
                ]
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

    '''Check in filtered_results if there are entries with same lemma but one has static paradigm
    (and matches the search).
    If yes, display only entry with static paradigm.
    (Maybe too many arrays, should make it more elegant!).'''
    entries_lemmaID_pos = []
    lemma_pos_array = []
    for entry, analyses in filtered_results:
        if entry:
            has_lemma_ref = entry.find('lg/lemma_ref')
        else:
            has_lemma_ref = None
        lemmaID = False
        pos = False
        lemma_pos_pair = []
        if has_lemma_ref is not None:
            entry_lemmaID = entry.find('lg/lemma_ref').attrib.get('lemmaID', False)
            lemmaID = entry_lemmaID.split('_')[0]
            pos = entry_lemmaID.split('_')[1].upper()
        for item in analyses:
            try:
                if [str(item.lemma), str(item.pos)] not in lemma_pos_pair:
                    lemma_pos_pair.append([str(item.lemma), str(item.pos)])
            except:
                if [item.lemma, item.pos] not in lemma_pos_pair:
                    lemma_pos_pair.append([item.lemma, item.pos])
        if len(lemma_pos_pair) == 1:
            lemma_pos_pair = lemma_pos_pair[0]
        entries_lemmaID_pos.append([entry, lemma_pos_pair, [lemmaID, pos]])
        lemma_pos_array.append([lemma_pos_pair, [lemmaID, pos]])

    final_results = []
    for var in lemma_pos_array:
        if var in lemma_pos_array and [[], var[0]] in lemma_pos_array:
            entries_lemmaID_pos.pop(lemma_pos_array.index(var))
            filtered_results.pop(lemma_pos_array.index(var))

    return filtered_results
