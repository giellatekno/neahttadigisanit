def decode_or_fail(string):
    try:
        return string.decode('utf-8')
    except:
        return string
