# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 Bartosz Kryza <bkryza@gmail.com>
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

from .decorator_utils import get_backend_decor, get_endpoint_decor
from .session import RestClientAsyncSession, RestClientSession
from .types import ArgsDict, AuthTypes, Backends
from .utils import normalize_url


class RestClient:
    """
    Base class for decorest REST clients.

    Method naming conventions for this class:
      - rule #1: do not restrict user's API
      - internal methods should be prefixed with '_'
      - user accessible methods should be suffixed with '_'
    """
    __backend: Backends
    __endpoint: str
    __client_args: typing.Any

    def __init__(self,
                 endpoint: typing.Optional[str] = None,
                 **kwargs: typing.Any):
        """Initialize the client with optional endpoint."""
        # First determine the preferred backend
        backend = None
        if 'backend' in kwargs:
            backend = kwargs['backend']
            del kwargs['backend']
        self.__backend = backend or get_backend_decor(self) or 'requests'

        # Check if the client arguments contain endpoint value
        self.__endpoint = endpoint  # type: ignore

        # Check if the other named arguments match the allowed arguments
        # for specified backend
        if self.__backend == 'requests':
            import requests
            valid_client_args = requests.Session.__attrs__
        elif self.__backend == 'httpx':
            import httpx
            import inspect
            valid_client_args \
                = inspect.getfullargspec(httpx.Client.__init__).kwonlyargs
        else:
            raise ValueError(f'Invalid backend: {self.backend_}')

        if not set(kwargs.keys()).issubset(set(valid_client_args)):
            raise ValueError(f'Invalid named arguments passed to the client: '
                             f'{set(kwargs.keys()) - set(valid_client_args)}')

        self.__client_args = kwargs

    def __getitem__(self, key: str) -> typing.Any:
        """Return named client argument."""
        return self._get_or_none(key)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        """Set named client argument."""
        self.__client_args[key] = value

    def __repr__(self) -> str:
        """Return instance representation."""
        return f'<{type(self).__name__} backend: {self.__backend} ' \
               f'endpoint: \'{self.__endpoint or get_endpoint_decor(self)}\'>'

    def session_(self, **kwargs: ArgsDict) -> RestClientSession:
        """
        Initialize RestClientSession session object.

        The `decorest` session object wraps a `requests` or `httpx`
         session object.

        Each valid API method defined in the API client can be called
        directly via the session object.
        """
        return RestClientSession(self, **kwargs)

    def async_session_(self, **kwargs: ArgsDict) -> RestClientAsyncSession:
        """
        Initialize RestClientAsyncSession session object.

        The `decorest` session object wraps a `requests` or `httpx`
        session object.

        Each valid API method defined in the API client can be called
        directly via the session object.
        """
        return RestClientAsyncSession(self, **kwargs)

    @property
    def backend_(self) -> str:
        """
        Get active backend.

        Returns the name of the active backend.
        """
        return self.__backend

    @property
    def endpoint_(self) -> str:
        """
        Get server endpoint.

        Returns the endpoint for the server, which was provided in the
        class decorator or in the client constructor arguments.
        """
        return self.__endpoint

    @property
    def client_args_(self) -> typing.Any:
        """
        Get arguments provided to client.

        Returns the dictionary with arguments that will be passed
        to session objects or requests. The dictionary keys depend
        on the backend:
          - for requests the valid keys are specified in:
              requests.Session.__attrs__
          - for httpx the valid keys are specified in the
            method:
              https.Client.__init__
        """
        return self.__client_args

    def _get_or_none(self, key: str) -> typing.Any:
        if key in self.__client_args:
            return self.__client_args[key]

        return None

    def build_path_(self, path_components: typing.List[str],
                    endpoint: typing.Optional[str]) -> str:
        """
        Build request path.

        Request is built by combining the endpoint with path
        components.
        """
        LOG.debug("Building request from path tokens: %s", path_components)

        if not endpoint:
            endpoint = self.__endpoint

        if not endpoint:
            raise ValueError("Server endpoint was not provided.")

        req = urllib.parse.urljoin(normalize_url(endpoint),
                                   "/".join(path_components))

        return req

    # here start the deprecated methods for compatibility
    def set_auth_(self, auth: AuthTypes) -> None:
        """Set authentication for the client."""
        self.__client_args['auth'] = auth

    def auth_(self) -> typing.Any:
        """Return the client authentication."""
        return self._get_or_none('auth')

    def _backend(self) -> str:
        """
        Get active backend [deprecated].

        Returns the name of the active backend.
        """
        return self.__backend

    def _auth(self) -> AuthTypes:
        """
        Get auth method if specified [deprecated].

        Returns the authentication object provided in the arguments.
        """
        return self.auth_()

    def _session(self) -> RestClientSession:
        return self.session_()

    def _async_session(self) -> RestClientAsyncSession:
        return self.async_session_()

    def _set_auth(self, auth: AuthTypes) -> None:
        self.set_auth_(auth)
