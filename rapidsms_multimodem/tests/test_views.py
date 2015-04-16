# coding: utf-8
from __future__ import unicode_literals
import copy

from django.core.urlresolvers import reverse

from rapidsms.tests.harness import RapidTest

from ..utils import unicode_to_ismsformat

# setup 2 modems on a iSMS multiport modem
MODEM_1 = {
    'ENGINE': 'rapidsms_multimodem.outgoing.MultiModemBackend',
    'sendsms_url': 'http://192.168.170.200:81/sendmsg',
    'sendsms_user': 'admin',
    'sendsms_pass': 'admin',
    'modem_port': 1,
    'server_slug': 'server-a',
}

MODEM_2 = copy.deepcopy(MODEM_1)
MODEM_2['modem_port'] = 2

# setup a third modem on a completely different iSMS server
MODEM_3 = copy.deepcopy(MODEM_1)
MODEM_3['sendsms_url'] = 'http://192.168.0.1/sendmsg'
MODEM_3['server_slug'] = 'server-b'


class MultimodemViewTest(RapidTest):

    urls = 'rapidsms_multimodem.tests.urls'
    disable_phases = True
    backends = {
        'backend-1': MODEM_1,
        'backend-2': MODEM_2,
        'server-b-backend': MODEM_3,
    }
    backend_url = reverse('multimodem-backend', kwargs={'server_slug': 'server-a'})

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
        response = self.client.post(self.backend_url, data)
        self.assertEqual(response.status_code, 400)

    def test_message_from_unknown_server(self):
        """HTTP 400 should return if server is not known to us."""
        data = {'XMLDATA': self.build_xml_request()}
        bad_url = reverse('multimodem-backend', kwargs={'server_slug': 'unknown'})
        response = self.client.post(bad_url, data)
        self.assertEqual(response.status_code, 400)

    def test_message_from_unknown_port_on_known_server(self):
        """HTTP 400 should return if port is not known to us."""
        data = {'XMLDATA': self.build_xml_request(message_params=[{
            'modem_number': 99,
        }])}
        bad_url = reverse('multimodem-backend', kwargs={'server_slug': 'server-a'})
        response = self.client.post(bad_url, data)
        self.assertEqual(response.status_code, 400)

    def test_improper_configuration_duplicate_server_port_combo(self):
        """HTTP 400 should return if server / port combo exist in more than 1 backend"""
        data = {'XMLDATA': self.build_xml_request()}
        # Misconfigure so that both backend-1 and backend-2 refer to port 1
        self.backends['backend-2']['modem_port'] = 1
        self.set_router()
        bad_url = reverse('multimodem-backend', kwargs={'server_slug': 'server-a'})
        response = self.client.post(bad_url, data)
        self.assertEqual(response.status_code, 400)
        # undo the misconfiguration for the rest of the testcases in this class
        self.backends['backend-2']['modem_port'] = 2
        self.set_router()

    def test_get_disabled(self):
        """HTTP 405 should return if GET is used."""
        data = {}
        response = self.client.get(self.backend_url, data)
        self.assertEqual(response.status_code, 405)

    def test_valid_post_one_message_single_port(self):
        """Valid POSTs should pass message object to router."""
        data = {'XMLDATA': self.build_xml_request()}
        response = self.client.post(self.backend_url, data)
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
        response = self.client.post(self.backend_url, data)
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
        response = self.client.post(self.backend_url, data)
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
        response = self.client.post(self.backend_url, data)
        self.assertEqual(response.status_code, 200)
        message1, message2 = self.inbound
        self.assertEqual('first message', message1.text)
        self.assertEqual('backend-1', message1.connection.backend.name)
        self.assertEqual('second message', message2.text)
        self.assertEqual('+19195551313', message2.connections[0].identity)
        self.assertEqual('backend-1', message2.connection.backend.name)

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
        response = self.client.post(self.backend_url, data)
        self.assertEqual(response.status_code, 200)
        message1, message2 = self.inbound
        self.assertEqual('port 1 message', message1.text)
        self.assertEqual('backend-1', message1.connection.backend.name)
        self.assertEqual('port 2 message', message2.text)
        self.assertEqual('backend-2', message2.connection.backend.name)

    def test_messages_from_different_servers_dont_get_confused(self):
        """Modem 1 on Server A is not confused for Modem 1 on Server B."""
        xmldata_a = self.build_xml_request()
        server_a_url = self.backend_url
        xmldata_b = self.build_xml_request()
        server_b_url = reverse('multimodem-backend', kwargs={'server_slug': 'server-b'})
        response_a = self.client.post(server_a_url, data={'XMLDATA': xmldata_a})
        self.assertEqual(response_a.status_code, 200)
        response_b = self.client.post(server_b_url, data={'XMLDATA': xmldata_b})
        self.assertEqual(response_b.status_code, 200)
        self.assertEqual(len(self.inbound), 2)
        message1, message2 = self.inbound
        self.assertEqual('backend-1', message1.connection.backend.name)
        self.assertEqual('server-b-backend', message2.connection.backend.name)
