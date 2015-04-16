import unittest

from rapidsms_multimodem import utils


class MultimodemFormatTest(unittest.TestCase):

    def setUp(self):
        self.unicode_string = 'The quick brown fox settled his disputes out of court.'
        self.isms_string = "0054;0068;0065;0020;0071;0075;0069;0063;006b;0020;0062;0072;006f;0077;" + \
                           "006e;0020;0066;006f;0078;0020;0073;0065;0074;0074;006c;0065;0064;0020;" + \
                           "0068;0069;0073;0020;0064;0069;0073;0070;0075;0074;0065;0073;0020;006f;" + \
                           "0075;0074;0020;006f;0066;0020;0063;006f;0075;0072;0074;002e;"

    def test_unicode_to_isms(self):
        self.assertEqual(utils.unicode_to_ismsformat(self.unicode_string), self.isms_string)

    def test_isms_to_unicode(self):
        self.assertEqual(utils.ismsformat_to_unicode(self.isms_string), self.unicode_string)

    def test_isms_to_unicode_8bit(self):
        """If iSMS sends 8bit characters, we support it."""
        self.assertEqual(utils.ismsformat_to_unicode('5468;65'), 'The')


class MultimodemURLEncodingTest(unittest.TestCase):

    def test_urlencode_text_key(self):
        """iSMS modem expects the value associated with the 'text' key to have its spaces replaced by '%20'."""
        query = {'key1': 'quote plus', 'key 2': 'quote plus'}
        self.assertIn('key1=quote+plus', utils.isms_urlencode(query))
        self.assertIn('key+2=quote+plus', utils.isms_urlencode(query))

    def test_urlencode_other_keys(self):
        """Other values (and all keys) should be URL encoded normally (space->'+')."""
        query = {'key1': 'quote plus', 'text': 'quote plus'}
        self.assertIn('key1=quote+plus', utils.isms_urlencode(query))
        self.assertIn('text=quote%20plus', utils.isms_urlencode(query))
