from django.test import TestCase
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse

from rapidsms.tests.harness import RapidTest

from rapidsms_multimodem.views import MultiModemView


VALID_POST = """<?xml version="1.0" encoding="ISO-8859-1"?>
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
