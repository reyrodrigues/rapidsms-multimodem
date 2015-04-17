import collections
import logging
import requests

from rapidsms.backends.base import BackendBase

from .utils import unicode_to_ismsformat, isms_urlencode

logger = logging.getLogger(__name__)

ISMS_ASCII = 0
ISMS_UNICODE = 2


class MultiModemBackend(BackendBase):
    """Outgoing SMS backend for MultiModem iSMS."""

    def configure(self, sendsms_url, sendsms_user, sendsms_pass, modem_port,
                  server_slug, sendsms_params=None):
        self.sendsms_url = sendsms_url
        self.sendsms_user = sendsms_user
        self.sendsms_pass = sendsms_pass
        self.modem_port = modem_port
        self.server_slug = server_slug
        self.sendsms_params = sendsms_params or {}

    def prepare_querystring(self, id_, text, identities, context):
        """Construct querystring to pass to requests.get."""
        to = ', '.join('"' + identity + '"' for identity in identities)
        # Send API requires a specific query params order
        params = collections.OrderedDict()
        params['user'] = self.sendsms_user
        params['passwd'] = self.sendsms_pass
        params['cat'] = 1
        params['enc'] = ISMS_ASCII
        params['modem'] = self.modem_port
        params['to'] = to
        # 'text' is tricky. iSMS has 3 encodings: ascii, enhanced ascii, and 'unicode'
        # (Note: it's not really Unicode, but a iSMS custom binary format)
        # we can't just use 'unicode' for everything because each encoding has character limits.
        # ascii = 160, enhanced_ascii = 140, unicode = 70
        # instead we'll check if it's ascii first, and use 'unicode' if it's not.
        # This code doesn't support 'enhanced ascii' at all.
        try:
            text.encode('ascii')
        except UnicodeEncodeError:
            params['enc'] = ISMS_UNICODE

        if params['enc'] == ISMS_ASCII:
            params['text'] = text
        else:
            params['text'] = unicode_to_ismsformat(text)
        params.update(self.sendsms_params)
        return isms_urlencode(params)

    def send(self, id_, text, identities, context={}):
        logger.debug('Sending message: %s' % text)

        # Splitting the identities because iSMS wasn't able to handle
        # identities in a single message.
        for identity in identities:
            # Maybe this needs to be paged
            # How do we handle a single failure?
            
            query_string = self.prepare_querystring(id_, text, [identity], context)
            r = requests.get(url=self.sendsms_url, params=query_string)
            if r.status_code != requests.codes.ok:
                r.raise_for_status()
            if "Err" in r.text:
                logger.error("Send API failed with %s" % r.text)
                logger.error("URL: %s" % r.url)
            logger.debug("URL: %s" % r.url)
