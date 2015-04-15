import logging
import xml.etree.ElementTree as ET

from django.conf import settings

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .utils import ismsformat_to_unicode

from rapidsms.router import receive
from rapidsms.router import lookup_connections
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def receive_multimodem_message(request):
    """
    The view to handle requests from multimodem has to be custom because the server can post 1-* messages in a single
    request. The Rapid built-in class-based views only accept a single message per form/post.

    TODO:
    Add basic auth to validate against Rapid's user database. The iSMS modem only supports basic auth.

    :param request:
    :return:
    """
    xml_data = request.POST.get('XMLDATA', '')
    """
    The modem posts the data as it receives it formatted as an xml file. The xml is then URL encoded and posted as a
    form parameter called XML data.

    Decoded Example:
    <?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>
    <Response>
        <Msg_Count>2</Msg_Count>
        <MessageNotification>
            <Message_Index>1</Message_Index>
            <ModemNumber>2:111222333</ModemNumber>
            <SenderNumber>+222333333</SenderNumber>
            <Date>15/04/13</Date>
            <Time>10:55:58</Time>
            <EncodingFlag>ASCII</EncodingFlag>
            <Message>Testn2</Message>
        </MessageNotification>
            <MessageNotification>
            <Message_Index>2</Message_Index>
            <ModemNumber>2:111222333</ModemNumber>
            <SenderNumber>+222333333</SenderNumber>
            <Date>15/04/13</Date>
            <Time>10:58:39</Time>
            <EncodingFlag>Unicode</EncodingFlag>
            <Message>0429043D043F0437043D043C0433043C0436043D043C</Message>
        </MessageNotification>
    </Response>
    """

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        logger.error("Failed to parse XML")
        logger.error(request)
        return HttpResponseBadRequest('Error parsing XML')

    for message in root.findall('MessageNotification'):
        raw_text = message.find('Message').text
        from_number = message.find('ModemNumber').text
        """
        Once we have the modem number we have to try to find its matching backend.
        Unfortunately, I'll have to dig through the settings.
        """
        if ':' in from_number:
            modem_number, phone_number = from_number.split(':')[0:2]
        else:
            # This is a single port modem
            modem_number = from_number

        possible_backends = getattr(settings, 'INSTALLED_BACKENDS', {}).items()
        """
        Obviously this needs refactoring.

        Two iSMS servers would have the same modem number.
        Another solution would be to add the phone number to the settings.
        """
        backend_names = [backend[0] for backend in possible_backends
                         if 'sendsms_params' in backend[1]
                         and 'modem' in backend[1]['sendsms_params']
                         and int(backend[1]['sendsms_params']['modem']) == int(modem_number)]
        if backend_names:
            backend_name = backend_names[0]
            encoding = message.find('EncodingFlag').text
            if encoding.lower() == "unicode":
                msg_text = ismsformat_to_unicode(raw_text)
            else:
                msg_text = raw_text

            connections = lookup_connections(backend_name, [message.find('SenderNumber').text])
            data = {'text': msg_text,
                    'connection': connections[0]}
            receive(**data)

    return HttpResponse('OK')
