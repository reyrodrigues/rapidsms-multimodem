from __future__ import unicode_literals
import logging
import xml.etree.ElementTree as ET

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from rapidsms.router import receive
from rapidsms.router import lookup_connections

from .utils import ismsformat_to_unicode

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def receive_multimodem_message(request, server_slug):
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

        # ModemNumber is simply 1 for single-port modems and it's a string of
        # 'port_numer:phone_number' for multiport modems.
        if ':' in from_number:
            modem_number, phone_number = from_number.split(':')[0:2]
        else:
            # This is a single port modem
            modem_number = from_number

        # Search through backends looking for the single one with this
        # server_slug / modem combo
        possible_backends = getattr(settings, 'INSTALLED_BACKENDS', {}).items()
        backend_names = [name for name, config in possible_backends
                         if str(config.get('modem_port')) == str(modem_number)
                         and config.get('server_slug') == server_slug]
        if backend_names:
            if len(backend_names) > 1:
                logger.error("More than 1 backend with this server/port combo: %s / %s",
                             server_slug, modem_number)
                return HttpResponseBadRequest('Improper Configuration: multiple backends with same server / port')
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
        else:
            logger.error("Can't find backend for this server/port combo: %s / %s",
                         server_slug, modem_number)
            return HttpResponseBadRequest('Unknown server or port.')

    return HttpResponse('OK')
