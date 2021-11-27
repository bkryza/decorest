# -*- coding: utf-8 -*-
#
# Copyright 2018-2021 Bartosz Kryza <bkryza@gmail.com>
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
"""
Base Http client implementation.

This module contains also some enums for HTTP protocol.
"""
import logging as LOG

import six
from six.moves.urllib.parse import urljoin

from .decorators import get_decor
from .utils import normalize_url


class RestClientSession(object):
    """Wrap a `requests` session for specific API client."""
    def __init__(self, client):
        """Initialize the session instance with a specific API client."""
        self.__client = client

        # Create a session of type specific for given backend
        if client._backend() == 'requests':
            import requests
            self.__session = requests.Session()
        else:
            import httpx
            self.__session = httpx.Client()

        if self.__client.auth is not None:
            self.__session.auth = self.__client.auth

    def __enter__(self):
        """Context manager initialization."""
        return self

    def __exit__(self, *args):
        """Context manager destruction."""
        self.__session.close()
        return False

    def __getattr__(self, name):
        """Forward any method invocation to actual client with session."""
        if name == '_requests_session':
            return self.__session

        if name == '_client':
            return self.__client

        if name == '_close':
            return self.__session.close

        def invoker(*args, **kwargs):
            kwargs['__session'] = self.__session
            return getattr(self.__client, name)(*args, **kwargs)

        return invoker


class RestClient(object):
    """Base class for decorest REST clients."""
    def __init__(self, endpoint=None, auth=None, backend='requests'):
        """Initialize the client with optional endpoint."""
        self.endpoint = get_decor(self, 'endpoint')
        self.auth = auth
        self._set_backend(backend)
        if endpoint is not None:
            self.endpoint = endpoint

    def _session(self):
        """
        Initialize RestClientSession session object.

        The `decorest` session object wraps a `requests` session object.

        Each valid API method defined in the API client can be called
        directly via the session object.
        """
        return RestClientSession(self)

    def _set_auth(self, auth):
        """
        Set a default authentication method for the client.

        Currently the object must be a proper subclass of
        `requests.auth.AuthBase` class.
        """
        self.auth = auth

    def _auth(self):
        """
        Get authentication object.

        Returns the authentication object set for this client.
        """
        return self.auth

    def _set_backend(self, backend):
        """
        Set preferred backend.

        This method allows to select which backend should be used for
        making actual HTTP[S] requests, currently supported are:
            * requests (default)
            * httpx

        The options should be passed as string.
        """
        if backend not in ('requests', 'httpx'):
            raise ValueError('{} backend not supported...'.format(backend))

        if backend == 'httpx' and six.PY2:
            raise ValueError('httpx backend is not supported on Python 2')

        self.backend = backend

    def _backend(self):
        """
        Get active backend.

        Returns the name of the active backend.
        """
        return self.backend

    def build_request(self, path_components=[]):
        """
        Build request.

        Request is built by combining the endpoint with path
        and query components.
        """
        LOG.debug("Building request from path tokens: %s", path_components)

        req = urljoin(normalize_url(self.endpoint), "/".join(path_components))

        return req
