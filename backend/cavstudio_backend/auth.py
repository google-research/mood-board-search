import hashlib
import json

from django.conf import settings
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class LocalhostAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        request_ip = get_client_ip(request)

        if not request_ip.startswith('127.'):
            raise AuthenticationFailed()

        return (LocalhostAuthentication.User('local'), None)

    class User:
        def __init__(self, username):
            self.username = username

        @property
        def is_authenticated(self):
            return True
