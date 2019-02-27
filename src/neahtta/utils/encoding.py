def encodeOrFail(S):
    try:
        return S.encode('utf-8')
    except:
        return S


def decode_or_fail(string):
    try:
        return string.decode('utf-8')
    except:
        return string
