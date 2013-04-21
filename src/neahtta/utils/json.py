def fmtForCallback(serialized_json, callback):
    if not callback:
        return serialized_json
    else:
        return "%s(%s)" % (callback, serialized_json)
