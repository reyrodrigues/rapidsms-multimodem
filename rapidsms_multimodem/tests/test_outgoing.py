# coding: utf-8
from __future__ import unicode_literals
from mock import patch

from django.test import TestCase

from rapidsms.tests.harness import CreateDataMixin

from rapidsms_multimodem.outgoing import MultiModemBackend, ISMS_ASCII, ISMS_UNICODE


class SendTest(CreateDataMixin, TestCase):

    def setUp(self):
        config = {
            'sendsms_url': 'http://192.168.170.200:81/sendmsg',
            'sendsms_user': 'admin',
            'sendsms_pass': 'admin',
            'sendsms_params': {'modem': 1},
        }
        self.backend = MultiModemBackend(None, "multimodem", **config)

    def test_required_fields(self):
        """Multimodem backend requires Gateway URL and credentials."""
        self.assertRaises(TypeError, MultiModemBackend, None, "multimodem")

    def test_prepare_querystring(self):
        message = self.create_outgoing_message(data={'text': 'a message'})
        query_string = self.backend.prepare_querystring(id_=message.id,
                                                        text=message.text,
                                                        identities=message.connections[0].identity,
                                                        context={})
        self.assertIn('user=admin', query_string)
        self.assertIn('passwd=admin', query_string)
        self.assertIn('enc={}'.format(ISMS_ASCII), query_string)
        self.assertIn('modem=1', query_string)
        # just ensure the text param is there. content is tested in test_utils.py
        self.assertIn('text=', query_string)

    def test_prepare_unicode_querystring(self):
        unicode_string = 'Щнпзнмгмжнм'
        message = self.create_outgoing_message(data={'text': unicode_string})
        query_string = self.backend.prepare_querystring(id_=message.id,
                                                        text=message.text,
                                                        identities=message.connections[0].identity,
                                                        context={})
        self.assertIn('enc={}'.format(ISMS_UNICODE), query_string)
        # just ensure the text param is there. content is tested in test_utils.py
        self.assertIn('text=', query_string)

    @patch('rapidsms_multimodem.outgoing.requests')
    def test_send(self, mock_requests):
        message = self.create_outgoing_message(data={'text': 'a message'})
        self.backend.send(id_=message.id,
                          text=message.text,
                          identities=message.connections[0].identity,
                          context={})
        self.assertTrue(mock_requests.get.called)
