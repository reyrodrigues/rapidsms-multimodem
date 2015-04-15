from django.conf.urls import patterns, url

from rapidsms_multimodem.views import receive_multimodem_message


urlpatterns = patterns(
    '',
    url(r"^backend/multimodem/$",
        receive_multimodem_message,
        name='multimodem-backend'),
)
