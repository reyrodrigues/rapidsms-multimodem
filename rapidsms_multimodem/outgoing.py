import copy
import logging
import requests
import collections
import pprint
import urllib

from rapidsms.backends.base import BackendBase


logger = logging.getLogger(__name__)


class MultiModemBackend(BackendBase):
    """Outgoing SMS backend for MultiModem iSMS."""

    def configure(self, sendsms_url, sendsms_user=None, sendsms_pass=None,
                  sendsms_params=None, **kwargs):
        self.sendsms_url = sendsms_url
        self.sendsms_user = sendsms_user
        self.sendsms_pass = sendsms_pass
        self.sendsms_params = sendsms_params or {}

    def prepare_request(self, id_, text, identities, context):
        """Construct outbound data for requests.get."""
        kwargs = {'url': self.sendsms_url}
        to = ', '.join('"' + identity + '"' for identity in identities)
        # Send API requires a specific query params order
        params = collections.OrderedDict()
        params['user'] = self.sendsms_user
        params['passwd'] = self.sendsms_pass
        params['cat'] = 1
        params['enc'] = self.sendsms_params.get('enc', 0)
        params['to'] = to
        # TODO: figure out how to make SMS %20 space delineated instead of +
        #       otherwise SMS is delivered as this+contains+spaces
        #       maybe use unicode encoding (enc) above?
        params['text'] = text
        params.update(self.sendsms_params)
        kwargs['params'] = params
        return kwargs

    def send(self, id_, text, identities, context={}):
        logger.debug('Sending message: %s' % text)
        kwargs = self.prepare_request(id_, text, identities, context)
        logger.debug('params: %s' % pprint.pformat(kwargs["params"]))
        r = requests.get(**kwargs)
        if r.status_code != requests.codes.ok:
            r.raise_for_status()
        if "Err" in r.text:
            logger.error("Send API failed with %s" % r.text)
            logger.error("URL: %s" % r.url)
        logger.debug("URL: %s" % r.url)
