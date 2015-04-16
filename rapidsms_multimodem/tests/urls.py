from django.conf.urls import url

from rapidsms_multimodem.views import receive_multimodem_message

urlpatterns = [
    url(r"^backend/multimodem/$", receive_multimodem_message, name='multimodem-backend'),
]
