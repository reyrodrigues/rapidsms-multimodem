from django.test import TestCase
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse

from rapidsms.tests.harness import RapidTest

from rapidsms_multimodem.views import MultiModemView


VALID_POST = """
<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>
<Response>
    <Msg_Count>1</Msg_Count>
    <MessageNotification>
        <Message_Index>1</Message_Index>
        <ModemNumber>2:111222333</ModemNumber>
        <SenderNumber>+222333444</SenderNumber>
        <Date>15/04/13</Date>
        <Time>10:54:27</Time>
        <EncodingFlag>ASCII</EncodingFlag>
        <Message>Test</Message>
    </MessageNotification>
</Response>
<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>
<Response>
    <Msg_Count>2</Msg_Count>
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
</Response>
<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>
<Response>
    <Msg_Count>1</Msg_Count>
    <MessageNotification>
        <Message_Index>1</Message_Index>
        <ModemNumber>2:380665717968</ModemNumber>
        <SenderNumber>+380990405272</SenderNumber>
        <Date>15/04/13</Date>
        <Time>11:01:16</Time>
        <EncodingFlag>Unicode</EncodingFlag>
        <Message>00C90020006F002000660069006D00200064006F0020006D0075006E0064006F002C002000650020006E00E3006F0020006D006500200069006D0070006F007200740061002E0020</Message>
    </MessageNotification>
</Response>
<?xml version="1.0" encoding="ISO-8859-1"?>
<Response>
<MessageNotification>
<ModemNumber>2:19525945092</ModemNumber>
<SenderNumber>6754535645</SenderNumber>
<Date>08/03/10</Date>
<Time>09:05:30</Time>
<Message>Here is a test message</Message>
</MessageNotification>
</Response>"""


urlpatterns = patterns('',  # nopep8
    url(r"^backend/multimodem/$",
        MultiModemView.as_view(backend_name='multimodem-backend'),
        name='multimodem-backend'),
)


class MultiModemViewTest(RapidTest):

    urls = 'rapidsms_multimodem.tests'
    disable_phases = True

    def test_valid_response_post(self):
        """HTTP 200 should return if data is valid."""
        response = self.client.post(reverse('multimodem-backend'),
                                    VALID_POST,
                                    content_type='text/xml')
        self.assertEqual(response.status_code, 200)
