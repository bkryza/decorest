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
import typing
import urllib.parse

from .decorator_utils import get_decor
from .session import RestClientAsyncSession, RestClientSession
from .types import AuthTypes, Backends
from .utils import normalize_url


class RestClient:
    """Base class for decorest REST clients."""
    def __init__(self,
                 endpoint: typing.Optional[str] = None,
                 auth: typing.Optional[AuthTypes] = None,
                 backend: Backends = 'requests'):
        """Initialize the client with optional endpoint."""
        self.endpoint = str(get_decor(self, 'endpoint'))
        self.auth = auth
        self._set_backend(backend)
        if endpoint is not None:
            self.endpoint = endpoint

    def _session(self) -> RestClientSession:
        """
        Initialize RestClientSession session object.

        The `decorest` session object wraps a `requests` or `httpx`
         session object.

        Each valid API method defined in the API client can be called
        directly via the session object.
        """
        return RestClientSession(self)

    def _async_session(self) -> RestClientAsyncSession:
        """
        Initialize RestClientAsyncSession session object.

        The `decorest` session object wraps a `requests` or `httpx`
        session object.

        Each valid API method defined in the API client can be called
        directly via the session object.
        """
        return RestClientAsyncSession(self)

    def _set_auth(self, auth: AuthTypes) -> None:
        """
        Set a default authentication method for the client.

        Currently the object must be a proper subclass of
        `requests.auth.AuthBase` class.
        """
        self.auth = auth

    def _auth(self) -> typing.Optional[AuthTypes]:
        """
        Get authentication object.

        Returns the authentication object set for this client.
        """
        return self.auth

    def _set_backend(self, backend: Backends) -> None:
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

        self.backend = backend

    def _backend(self) -> str:
        """
        Get active backend.

        Returns the name of the active backend.
        """
        return self.backend

    def build_request(self, path_components: typing.List[str]) -> str:
        """
        Build request.

        Request is built by combining the endpoint with path
        and query components.
        """
        LOG.debug("Building request from path tokens: %s", path_components)

        req = urllib.parse.urljoin(normalize_url(self.endpoint),
                                   "/".join(path_components))

        return req
