Getting Started and Setup
=========================

Below are the basic steps need to get rapidsms-multimodem integrated into your
RapidSMS project.


MultiModem Setup
----------------

Log into the MultiModem Web Management system and:

* Enable HTTP API Status under ``SMS Services (top nav) > SMS API (sidebar nav) > HTTP API Configuration``. Make sure you click Save.
* Add a new SMS user under ``SMS Services (top nav) > Users (sidebar nav)``.
* Enable Non Polling Receive API Status under ``SMS Services (top nav) > SMS API (sidebar nav) > Non Polling Receive API Configuration``. Once saved, fill in the following fields:
    * **Server:** Server URI or hosname. For local development, this will most likely just be your IP address, e.g. ``192.168.1.100``.
    * **Port:** Either ``8000`` for local development or ``80`` for production.
    * **Server Default Page:** You backend URL as defined below, e.g. ``backend/multimodem/``


RapidSMS Setup
--------------

Install ``rapidsms-multimodem``::

    pip install rapidsms-multimodem

Add ``rapidsms_multimodem`` to your ``INSTALLED_APPS`` in your ``settings.py``
file:

.. code-block:: python
    :emphasize-lines: 3

    INSTALLED_APPS = (
        # other apps
        'rapidsms_multimodem',
    )



Add the following to your existing ``INSTALLED_BACKENDS`` configuration in your
``settings.py`` file:

.. code-block:: python
    :emphasize-lines: 4-9

    INSTALLED_BACKENDS = {
        # ...
        # other backends, if any
        "multimodem-backend": {
            "ENGINE":  "rapidsms_multimodem.outgoing.MultiModemBackend",
            "sendsms_url": "http://<multimodem-ip-address>:81/sendmsg",
            "sendsms_user": "<username>",
            "sendsms_pass": "<password>",
        },
    }

Next, you need to add an endpoint to your ``urls.py`` for the newly created
backend.  You can do this like so:

.. code-block:: python
    :emphasize-lines: 6-7

    from django.conf.urls import patterns, include, url
    from rapidsms_multimodem.views import MultiModemBackend

    urlpatterns = patterns('',
        # ...
        url(r"^backend/multimodem/$",
            MultiModemBackend.as_view(backend_name="multimodem-backend")),
    )

Now inbound MultiModem messages can be received at 
``<your-server>/backend/multimodem/`` and outbound messages will be 
sent via the MultiModem backend.
