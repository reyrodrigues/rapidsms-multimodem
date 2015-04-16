import urllib


def unicode_to_ismsformat(unicode_str):
    """
    Example:
    text_to_ismsformat('The quick brown fox settled his disputes out of court.')
    ->  "0054;0068;0065;0020;0071;0075;0069;0063;006B;0020;0062;0072;006F;0077;
         006E;0020;0066;006F;0078;0020;0073;0065;0074;0074;006C;0065;0064;0020;
         0068;0069;0073;0020;0064;0069;0073;0070;0075;0074;0065;0073;0020;006F;
         0075;0074;0020;006F;0066;0020;0063;006F;0075;0072;0074;002E;"
    """
    encoded = unicode(unicode_str).encode('utf-16be')
    encoded_array = bytearray(encoded)
    byte_str = ""
    for i in xrange(0, len(encoded_array), 2):
        byte_str += "%02x%02x;" % (encoded_array[i], encoded_array[i + 1])
    return byte_str


def ismsformat_to_unicode(byte_str):
    """
    Reverses the formatting performed by unicode_to_ismsformat.
    """
    unformatted = byte_str.replace(';', '')
    unicode_str = unicode()
    if (len(unformatted) % 4) == 0:
        for i in xrange(0, len(unformatted), 4):
            unicode_str += unichr(int(unformatted[i] +
                                      unformatted[i + 1] +
                                      unformatted[i + 2] +
                                      unformatted[i + 3], 16))
    elif (len(unformatted) % 2) == 0:
        for i in xrange(0, len(unformatted), 2):
            unicode_str += unichr(int(unformatted[i] +
                                      unformatted[i + 1], 16))
    return unicode_str


def isms_urlencode(query):
    """Encode a dictionary into a URL query string.

    Customized because `text` parameter must have space characters quoted with %20 instead of +
    Everything else has to be encoded with quote_plus
    """
    parts = []
    for k, v in query.items():
        k = urllib.quote_plus(str(k))
        # text keyword must be quoted with spaces converted to '%20', not '+'
        if k == 'text':
            v = urllib.quote(str(v))
        else:
            v = urllib.quote_plus(str(v))
        parts.append(k + '=' + v)
    return '&'.join(parts)
