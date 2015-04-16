# coding: utf-8
from __future__ import unicode_literals

from django.test import TestCase

from rapidsms.tests.harness import CreateDataMixin

from rapidsms_multimodem.outgoing import MultiModemBackend, ISMS_UNICODE
from rapidsms_multimodem.utils import unicode_to_ismsformat


class SendTest(CreateDataMixin, TestCase):

    def test_required_fields(self):
        """Multimodem backend requires Gateway URL and credentials."""
        self.assertRaises(TypeError, MultiModemBackend, None, "multimodem")

    def test_prepare_request(self):
        message = self.create_outgoing_message(data={'text': 'a message'})
        config = {
            'sendsms_url': 'http://192.168.170.200:81/sendmsg',
            'sendsms_user': 'admin',
            'sendsms_pass': 'admin',
            'sendsms_params': {'modem': 1},
        }
        backend = MultiModemBackend(None, "multimodem", **config)
        data = backend.prepare_request(id_=message.id,
                                       text=message.text,
                                       identities=message.connections[0].identity,
                                       context={})
        self.assertTrue('url' in data)
        self.assertTrue('params' in data)
        self.assertEqual(data['params']['text'], 'a message')

    def test_prepare_unicode_request(self):
        unicode_string = 'Щнпзнмгмжнм'
        message = self.create_outgoing_message(data={'text': unicode_string})
        config = {
            'sendsms_url': 'http://192.168.170.200:81/sendmsg',
            'sendsms_user': 'admin',
            'sendsms_pass': 'admin',
            'sendsms_params': {'modem': 1},
        }
        backend = MultiModemBackend(None, "multimodem", **config)
        data = backend.prepare_request(id_=message.id,
                                       text=message.text,
                                       identities=message.connections[0].identity,
                                       context={})
        self.assertTrue('url' in data)
        self.assertTrue('params' in data)
        self.assertEqual(data['params']['enc'], ISMS_UNICODE)
        self.assertEqual(data['params']['text'], unicode_to_ismsformat(unicode_string))

    import mock

    @mock.patch('rapidsms_multimodem.outgoing.requests')
    def test_send(self, mock_requests):
        message = self.create_outgoing_message(data={'text': 'a message'})
        config = {
            'sendsms_url': 'http://192.168.170.200:81/sendmsg',
            'sendsms_user': 'admin',
            'sendsms_pass': 'admin',
            'sendsms_params': {'modem': 1},
        }
        backend = MultiModemBackend(None, "multimodem", **config)
        backend.send(id_=message.id,
                     text=message.text,
                     identities=message.connections[0].identity,
                     context={})
        self.assertTrue(mock_requests.get.called)

    # def test_outgoing_unicode_characters(self):
    #     """Ensure outgoing messages are encoded properly."""
    #     data = {'text': self.random_unicode_string(20)}
    #     message = self.create_outgoing_message(data=data)
    #     config = {'number': '+12223334444',
    #               'account_sid': self.random_string(34),
    #               'auth_token': self.random_string(34),
    #               'encoding': 'UTF-8'}
    #     backend = TwilioBackend(None, "twilio", config=config)
    #     data = backend.prepare_message(id_=message.id, text=message.text,
    #                                    identities=message.connections[0].identity,
    #                                    context={})
    #     self.assertEqual(data['body'].decode('UTF-8'), message.text)
