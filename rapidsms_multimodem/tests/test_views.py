# coding: utf-8
from __future__ import unicode_literals
import copy

from django.core.urlresolvers import reverse

from rapidsms.tests.harness import RapidTest

from ..utils import unicode_to_ismsformat

# setup 2 ports on a iSMS multiport modem
MODEM_1 = {
    'ENGINE': 'rapidsms_multimodem.outgoing.MultiModemBackend',
    'sendsms_url': 'http://192.168.170.200:81/sendmsg',
    'sendsms_user': 'admin',
    'sendsms_pass': 'admin',
    'sendsms_params': {'modem': 1},
}

MODEM_2 = copy.deepcopy(MODEM_1)
MODEM_2['sendsms_params']['modem'] = 2


class MultimodemViewTest(RapidTest):

    urls = 'rapidsms_multimodem.tests.urls'
    disable_phases = True
    backends = {
        'backend-1': MODEM_1,
        'backend-2': MODEM_2,
    }

    def build_xml_request(self, n=1, message_params=None):
        """Build a valid iSMS XML request.

        Without params, it will build a request with a single message, as specified by `defaults`.

        Provide `n` to include more than 1 message in a single request.

        Provide a list of dictionaries in `message_params` to customize each message. If `n` is
        greater than the length of `message_params`, then defaults will be used for the remaining
        messages.
        """
        defaults = {
            'modem_number': '1',
            'sender_number': '+19195551212',
            'encoding_flag': 'ASCII',
            'message': 'a test message',
            'date': '15/04/14',
            'time': '13:50:19',
        }
        one_message_template = """
        <MessageNotification>
          <Message_Index>{index}</Message_Index>
          <ModemNumber>{modem_number}</ModemNumber>
          <SenderNumber>{sender_number}</SenderNumber>
          <Date>{date}</Date>
          <Time>{time}</Time>
          <EncodingFlag>{encoding_flag}</EncodingFlag>
          <Message>{message}</Message>
        </MessageNotification>"""
        response_template = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <Response>
          <Msg_Count>{count}</Msg_Count>
          {messages_as_xml}
        </Response>"""

        messages_as_xml = ""
        for i in range(n):
            data = defaults.copy()
            if message_params and len(message_params) > i:
                data.update(message_params[i])
            messages_as_xml += one_message_template.format(index=i + 1, **data)
        return response_template.format(count=n, messages_as_xml=messages_as_xml)

    def test_invalid_response(self):
        """HTTP 400 should return if data is invalid."""
        data = {}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 400)

    def test_get_disabled(self):
        """HTTP 405 should return if GET is used."""
        data = {}
        response = self.client.get(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 405)

    def test_valid_post_one_message_single_port(self):
        """Valid POSTs should pass message object to router."""
        data = {'XMLDATA': self.build_xml_request()}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 200)
        message = self.inbound[0]
        self.assertEqual('a test message', message.text)
        self.assertEqual('+19195551212', message.connections[0].identity)
        self.assertEqual('backend-1', message.connection.backend.name)

    def test_valid_post_one_message_multiport(self):
        """Multiport modems have a slightly different format for ModemNumber."""
        xmldata = self.build_xml_request(message_params=[
            {
                'modem_number': '1:9195551111',
            }
        ])
        data = {'XMLDATA': xmldata}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 200)
        message = self.inbound[0]
        self.assertEqual('a test message', message.text)
        self.assertEqual('+19195551212', message.connections[0].identity)
        self.assertEqual('backend-1', message.connection.backend.name)

    def test_valid_unicode_message(self):
        unicode_string = 'Щнпзнмгмжнм'
        isms_encoded_string = unicode_to_ismsformat(unicode_string)
        xmldata = self.build_xml_request(message_params=[
            {
                'encoding_flag': 'Unicode',
                'message': isms_encoded_string,
            }
        ])
        data = {'XMLDATA': xmldata}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 200)
        message = self.inbound[0]
        self.assertEqual(unicode_string, message.text)
        self.assertEqual('+19195551212', message.connections[0].identity)
        self.assertEqual('backend-1', message.connection.backend.name)

    def test_valid_post_two_messages_single_port(self):
        """Modem can send more than 1 message in a request."""
        xmldata = self.build_xml_request(n=2, message_params=[
            {
                'message': 'first message'
            },
            {
                'message': 'second message',
                'sender_number': '+19195551313',
            }
        ])
        data = {'XMLDATA': xmldata}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.inbound), 2)
        message = self.inbound[0]
        self.assertEqual('first message', message.text)
        self.assertEqual('backend-1', message.connection.backend.name)
        message = self.inbound[1]
        self.assertEqual('second message', message.text)
        self.assertEqual('+19195551313', message.connections[0].identity)
        self.assertEqual('backend-1', message.connection.backend.name)

    def test_messages_from_different_ports_get_to_different_backends(self):
        xmldata = self.build_xml_request(n=2, message_params=[
            {
                'message': 'port 1 message',
                'modem_number': '1:9995551111',
            },
            {
                'message': 'port 2 message',
                'modem_number': '2:9995552222',
            }
        ])
        data = {'XMLDATA': xmldata}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.inbound), 2)
        message = self.inbound[0]
        self.assertEqual('port 1 message', message.text)
        self.assertEqual('backend-1', message.connection.backend.name)
        message = self.inbound[1]
        self.assertEqual('port 2 message', message.text)
        self.assertEqual('backend-2', message.connection.backend.name)
