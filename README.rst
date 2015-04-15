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

"multimodem-1": {
"ENGINE": "rapidsms_multimodem.outgoing.MultiModemBackend",
    "sendsms_url": "http://192.168.170.200:81/sendmsg",
    "sendsms_user": "admin",
    "sendsms_pass": "admin",
    "sendsms_params": { "modem": 1 },
},


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

.. |coverage| image:: https://coveralls.io/repos/theirc/rapidsms-multimodem/badge.svg?branch=master
    :alt: coverage report
    :scale: 100%
    :target: https://coveralls.io/r/theirc/rapidsms-multimodem?branch=master

.. |docs| image:: https://readthedocs.org/projects/rapidsms-multimodem/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: http://rapidsms-multimodem.readthedocs.org/
