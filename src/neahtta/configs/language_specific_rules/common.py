
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

