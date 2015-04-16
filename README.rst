rapidsms-multimodem
===================

|build-status| |coverage| |docs|

`MultiModem iSMS`_ backend for the `RapidSMS`_ project.


License
-------

rapidsms-multimodem is released under the BSD License. See the  `LICENSE
<https://github.com/caktus/rapidsms-multimodem/blob/master/LICENSE.txt>`_ file
for more details.

Settings
--------

The following parameters are required: ``sendsms_url``, ``sendsms_user``, ``sendsms_pass``,
``modem_port``, and ``server_slug``::

  "multimodem-1": {
      "ENGINE": "rapidsms_multimodem.outgoing.MultiModemBackend",
      "sendsms_url": "http://192.168.170.200:81/sendmsg",
      "sendsms_user": "admin",
      "sendsms_pass": "admin",
      "modem_port": 1,
      "server_slug": "isms-lebanon",
  },

Single port modems only have 1 port, but it should still be specified.

The ``server_slug`` parameter serves 2 purposes. It uniquely identifies the iSMS server, so that
RapidSMS doesn't get confused by 2 different servers having the same port number (since those are
restricted to be integers from 1 to 8). It's also used to create the RapidSMS URL that the iSMS
server will send messages to. Your ``urls.py`` should look something like this::

  urlpatterns = [
      url(r"^backend/multimodem/(?P<server_slug>[\w_-]+)/$",
          receive_multimodem_message,
          name='multimodem-backend'),
  ]

With the 2 code examples above, your iSMS server should POST messages to
http://your-rapidsms-server.example.com/backend/multimodem/isms-lebanon/.


Contributing
------------

If you think you've found a bug or are interested in contributing to this
project check out `rapidsms-multimodem on Github <https://github.com/caktus
/rapidsms-multimodem>`_.

Development by `Caktus Consulting Group <http://www.caktusgroup.com/>`_.


.. _RapidSMS: http://www.rapidsms.org/
.. _MultiModem iSMS: http://www.multitech.com/en_US/PRODUCTS/Families/MultiModemiSMS/

.. |build-status| image:: https://travis-ci.org/caktus/rapidsms-multimodem.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/caktus/rapidsms-multimodem

.. |coverage| image:: https://coveralls.io/repos/caktus/rapidsms-multimodem/badge.svg?branch=master
    :alt: coverage report
    :scale: 100%
    :target: https://coveralls.io/r/caktus/rapidsms-multimodem?branch=master

.. |docs| image:: https://readthedocs.org/projects/rapidsms-multimodem/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: http://rapidsms-multimodem.readthedocs.org/
