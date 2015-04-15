from __future__ import unicode_literals

from django.core.urlresolvers import reverse

from rapidsms.tests.harness import RapidTest


EXAMPLE_CONFIG = {
    'ENGINE': 'rapidsms_multimodem.outgoing.MultiModemBackend',
    'sendsms_url': 'http://192.168.170.200:81/sendmsg',
    'sendsms_user': 'admin',
    'sendsms_pass': 'admin',
    'sendsms_params': {'modem': 1},
}

VALID_POST = """<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>
<Response>
<Msg_Count>3</Msg_Count>
<MessageNotification>
<Message_Index>1</Message_Index>
<ModemNumber>2:380665717968</ModemNumber>
<SenderNumber>+380990405272</SenderNumber>
<Date>15/04/13</Date>
<Time>10:55:58</Time>
<EncodingFlag>ASCII</EncodingFlag>
<Message>Testn2</Message>
</MessageNotification>
<MessageNotification>
<Message_Index>2</Message_Index>
<ModemNumber>2:380665717968</ModemNumber>
<SenderNumber>+380990405272</SenderNumber>
<Date>15/04/13</Date>
<Time>10:58:39</Time>
<EncodingFlag>Unicode</EncodingFlag>
<Message>0429043D043F0437043D043C0433043C0436043D043C</Message>
</MessageNotification>
<MessageNotification>
<Message_Index>3</Message_Index>
<ModemNumber>2:380665717968</ModemNumber>
<SenderNumber>+380990405272</SenderNumber>
<Date>15/04/13</Date>
<Time>11:01:16</Time>
<EncodingFlag>Unicode</EncodingFlag>
<Message>00C90020006F002000660069006D00200064006F0020006D0075006E0064006F002C002000650020006E00E3006F0020006D006500200069006D0070006F007200740061002E0020</Message>
</MessageNotification>
</Response>
"""

ONE_GOOD_MESSAGE = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Response>
<Msg_Count>1</Msg_Count>
<MessageNotification>
<Message_Index>1</Message_Index>
<ModemNumber>1</ModemNumber>
<SenderNumber>+19195551212</SenderNumber>
<Date>15/04/14</Date>
<Time>13:50:19</Time>
<EncodingFlag>ASCII</EncodingFlag>
<Message>a test message</Message>
</MessageNotification>
</Response>
"""

TWO_GOOD_MESSAGES = """<?xml version="1.0" encoding="ISO-8859-1"?>
<Response>
<Msg_Count>2</Msg_Count>
<MessageNotification>
<Message_Index>1</Message_Index>
<ModemNumber>1</ModemNumber>
<SenderNumber>+19195551212</SenderNumber>
<Date>15/04/14</Date>
<Time>13:50:19</Time>
<EncodingFlag>ASCII</EncodingFlag>
<Message>a test message</Message>
</MessageNotification>
<MessageNotification>
<Message_Index>2</Message_Index>
<ModemNumber>1</ModemNumber>
<SenderNumber>+19195551313</SenderNumber>
<Date>15/04/14</Date>
<Time>13:51:19</Time>
<EncodingFlag>ASCII</EncodingFlag>
<Message>a second message</Message>
</MessageNotification>
</Response>
"""


class MultimodemViewTest(RapidTest):

    urls = 'rapidsms_multimodem.tests.urls'
    disable_phases = True
    backends = {
        'multimodem-backend': EXAMPLE_CONFIG,
    }

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

    def test_valid_post_one_message(self):
        """Valid POSTs should pass message object to router."""
        data = {'XMLDATA': ONE_GOOD_MESSAGE}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 200)
        message = self.inbound[0]
        self.assertEqual('a test message', message.text)
        self.assertEqual('+19195551212', message.connections[0].identity)
        self.assertEqual('multimodem-backend', message.connection.backend.name)

    def test_valid_post_two_messages(self):
        """Modem can send more than 1 message in a request."""
        data = {'XMLDATA': TWO_GOOD_MESSAGES}
        response = self.client.post(reverse('multimodem-backend'), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.inbound), 2)
        message = self.inbound[0]
        self.assertEqual('a test message', message.text)
        self.assertEqual('+19195551212', message.connections[0].identity)
        self.assertEqual('multimodem-backend', message.connection.backend.name)
        message = self.inbound[1]
        self.assertEqual('a second message', message.text)
        self.assertEqual('+19195551313', message.connections[0].identity)
        self.assertEqual('multimodem-backend', message.connection.backend.name)

    # def test_valid_post_three_messages(self):
    #     """Modem can send more than 1 message in a request."""
    #     data = {'XMLDATA': VALID_POST}
    #     response = self.client.post(reverse('multimodem-backend'), data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(self.inbound), 2)
    #     message = self.inbound[0]
    #     self.assertEqual('a test message', message.text)
    #     self.assertEqual('+19195551212', message.connections[0].identity)
    #     self.assertEqual('multimodem-backend', message.connection.backend.name)
    #     message = self.inbound[1]
    #     self.assertEqual('a second message', message.text)
    #     self.assertEqual('+19195551313', message.connections[0].identity)
    #     self.assertEqual('multimodem-backend', message.connection.backend.name)
