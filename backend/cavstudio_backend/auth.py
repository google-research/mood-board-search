# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
