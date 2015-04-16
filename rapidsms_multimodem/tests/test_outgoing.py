# coding: utf-8
from __future__ import unicode_literals
from mock import patch

from django.test import TestCase

from rapidsms.tests.harness import CreateDataMixin

from rapidsms_multimodem.outgoing import MultiModemBackend, ISMS_UNICODE
from rapidsms_multimodem.utils import unicode_to_ismsformat


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

    def test_prepare_request(self):
        message = self.create_outgoing_message(data={'text': 'a message'})
        data = self.backend.prepare_request(id_=message.id,
                                            text=message.text,
                                            identities=message.connections[0].identity,
                                            context={})
        self.assertTrue('url' in data)
        self.assertTrue('params' in data)
        self.assertEqual(data['params']['text'], 'a message')

    def test_prepare_unicode_request(self):
        unicode_string = 'Щнпзнмгмжнм'
        message = self.create_outgoing_message(data={'text': unicode_string})
        data = self.backend.prepare_request(id_=message.id,
                                            text=message.text,
                                            identities=message.connections[0].identity,
                                            context={})
        self.assertTrue('url' in data)
        self.assertTrue('params' in data)
        self.assertEqual(data['params']['enc'], ISMS_UNICODE)
        self.assertEqual(data['params']['text'], unicode_to_ismsformat(unicode_string))

    @patch('rapidsms_multimodem.outgoing.requests')
    def test_send(self, mock_requests):
        message = self.create_outgoing_message(data={'text': 'a message'})
        self.backend.send(id_=message.id,
                          text=message.text,
                          identities=message.connections[0].identity,
                          context={})
        self.assertTrue(mock_requests.get.called)
