# -*- coding: utf-8 -*-
#
# Copyright 2018 Bartosz Kryza <bkryza@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging as LOG
import re
from six.moves.urllib.parse import urlencode, urljoin
from .utils import normalize_url


def render_path(path, args):
    """
    Render REST path from *args
    """
    LOG.debug('RENDERING PATH FROM: %s,  %s', path, args)
    result = path
    matches = re.search(r'{([^}.]*)}', result)
    while matches:
        path_token = matches.group(1)
        if path_token not in args:
            raise ValueError("Missing argument %s in REST call" % (path_token))
        result = re.sub('{%s}' % (path_token), str(args[path_token]), result)
        matches = re.search(r'{([^}.]*)}', result)
    return result


class HttpMethod(object):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'


class HttpStatus(object):
    ANY = 99999


class RestClient(object):
    """
    Base class for decorest REST clients.
    """

    def __init__(self, endpoint=None):
        self.endpoint = endpoint

    def start_session(self):
        """
        Initializes 'requests' session object. All consecutive requests
        will go via the session object.

        If this method is not called on the client, the requests will be
        performed using standard requests without a session.
        """
        pass

    def stop_session(self):
        """
        Stops the requests session, i.e. all consecutive requests will be
        called using standard requests without session object.
        """
        pass

    def build_request(self, path_components=[]):
        """
        Builds request by combining the endpoint with path
        and query components.
        """
        LOG.debug("Building request from path tokens: %s", path_components)

        req = urljoin(normalize_url(self.endpoint), "/".join(path_components))

        return req
