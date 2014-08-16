import logging
import xml.etree.ElementTree as ET

from rapidsms.backends.http.views import GenericHttpBackendView


logger = logging.getLogger(__name__)


class MultiModemView(GenericHttpBackendView):
    """
    Backend view for processing incoming messages from MultiModem iSMS.
    """

    http_method_names = ['post']

    def get_form_kwargs(self):
        """Load XML POST data."""
        kwargs = super(MultiModemView, self).get_form_kwargs()
        xml = kwargs['data']['XMLDATA']
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            logger.error("Failed to parse XML")
            logger.error(self.request.body)
        for message in root.findall('MessageNotification'):
            data = {'text': message.find('Message').text,
                    'identity': message.find('SenderNumber').text}
        kwargs['data'] = data
        return kwargs
