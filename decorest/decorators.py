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
"""Decorators implementation.

Each RestClient subclass has a `__decorest__` property storing
a dictionary with decorator values provided by decorators
added to the client class or method.
"""

import inspect
import numbers
import typing
from operator import methodcaller

from . import types
from .decorator_utils import set_decor, set_header_decor
from .errors import HTTPErrorWrapper
from .request import HttpRequest
from .types import Backends, HttpMethod, HttpStatus, TDecor
from .utils import CaseInsensitiveDict


def on(status: typing.Union[types.ellipsis, int],
       handler: typing.Callable[..., typing.Any]) \
        -> typing.Callable[[TDecor], TDecor]:
    """
    On status result handlers decorator.

    The handler is a function or lambda which will receive as
    the sole parameter the requests response object.
    """
    def on_decorator(t: TDecor) -> TDecor:
        if status is Ellipsis:  # type: ignore
            set_decor(t, 'on', {HttpStatus.ANY: handler})
        elif isinstance(status, numbers.Integral):
            set_decor(t, 'on', {status: handler})
        else:
            raise TypeError(
                "Status in @on decorator must be integer or '...'.")
        return t

    return on_decorator


def query(name: str, value: typing.Optional[str] = None) \
        -> typing.Callable[[TDecor], TDecor]:
    """Query parameter decorator."""
    def query_decorator(t: TDecor) -> TDecor:
        value_ = value
        if inspect.isclass(t):
            raise TypeError("@query decorator can only be "
                            "applied to methods.")

        set_decor(t, 'query', {name: value_ or name})
        return t

    return query_decorator


def form(name: str, value: typing.Optional[str] = None) \
        -> typing.Callable[[TDecor], TDecor]:
    """Form parameter decorator."""
    def form_decorator(t: TDecor) -> TDecor:
        value_ = value
        if inspect.isclass(t):
            raise TypeError("@form decorator can only be "
                            "applied to methods.")

        set_decor(t, 'form', {name: value_ or name})
        return t

    return form_decorator


def multipart(name: str, value: typing.Optional[str] = None) \
        -> typing.Callable[[TDecor], TDecor]:
    """Multipart parameter decorator."""
    def multipart_decorator(t: TDecor) -> TDecor:
        value_ = value
        if inspect.isclass(t):
            raise TypeError("@multipart decorator can only be "
                            "applied to methods.")

        set_decor(t, 'multipart', {name: value_ or name})
        return t

    return multipart_decorator


def header(name: str, value: typing.Optional[str] = None) \
        -> typing.Callable[[TDecor], TDecor]:
    """Header class and method decorator."""
    def header_decorator(t: TDecor) -> TDecor:
        set_header_decor(t, CaseInsensitiveDict({name: value or name}))
        return t

    return header_decorator


def endpoint(value: str) -> typing.Callable[[TDecor], TDecor]:
    """Endpoint class and method decorator."""
    def endpoint_decorator(t: TDecor) -> TDecor:
        set_decor(t, 'endpoint', value)
        return t

    return endpoint_decorator


def content(value: str) -> typing.Callable[[TDecor], TDecor]:
    """Content-type header class and method decorator."""
    def content_decorator(t: TDecor) -> TDecor:
        set_header_decor(t, CaseInsensitiveDict({'Content-Type': value}))
        return t

    return content_decorator


def accept(value: str) -> typing.Callable[[TDecor], TDecor]:
    """Accept header class and method decorator."""
    def accept_decorator(t: TDecor) -> TDecor:
        set_header_decor(t, CaseInsensitiveDict({'Accept': value}))
        return t

    return accept_decorator


def body(name: str,
         serializer: typing.Optional[typing.Callable[..., typing.Any]] = None) \
        -> typing.Callable[[TDecor], TDecor]:
    """
    Body parameter decorator.

    Determines which method argument provides the body.
    """
    def body_decorator(t: TDecor) -> TDecor:
        set_decor(t, 'body', (name, serializer))
        return t

    return body_decorator


def timeout(value: float) -> typing.Callable[[TDecor], TDecor]:
    """
    Timeout parameter decorator.

    Specifies a default timeout value for method or entire API.
    """
    def timeout_decorator(t: TDecor) -> TDecor:
        set_decor(t, 'timeout', value)
        return t

    return timeout_decorator


def stream(t: TDecor) -> TDecor:
    """
    Stream parameter decorator, takes boolean True or False.

    If specified, adds `stream=value` to requests and the value returned
    from such method will be the requests object.
    """
    set_decor(t, 'stream', True)
    return t


def backend(value: Backends) -> typing.Callable[[TDecor], TDecor]:
    """
    Specify default backend for the client.

    Without this decorator, default backend is 'requests'.
    This decorator is only applicable to client classes.
    """
    def backend_decorator(t: TDecor) -> TDecor:
        if not inspect.isclass(t):
            raise TypeError("@backend decorator can only be "
                            "applied to classes.")
        set_decor(t, 'backend', value)
        return typing.cast(TDecor, t)

    return backend_decorator


class HttpMethodDecorator:
    """Abstract decorator for HTTP method decorators."""
    def __init__(self, path: str):
        """Initialize decorator with endpoint relative path."""
        self.path_template = path

    async def call_async(self, func: typing.Callable[..., typing.Any],
                         *args: typing.Any,
                         **kwargs: typing.Any) -> typing.Any:
        """Execute async HTTP request."""
        http_request = HttpRequest(func, self.path_template, args, kwargs)

        try:
            if http_request.http_method == HttpMethod.GET \
                    and http_request.is_stream:
                del kwargs['stream']
                follow_redirects = True
                if 'follow_redirects' in http_request.kwargs:
                    follow_redirects = http_request.kwargs['follow_redirects']
                    del http_request.kwargs['follow_redirects']

                req = http_request.execution_context.build_request(
                    'GET', http_request.req, **http_request.kwargs)

                result = await http_request.\
                    execution_context.send(req,
                                           stream=True,
                                           follow_redirects=follow_redirects)
            else:
                if http_request.http_method == HttpMethod.POST \
                        and http_request.is_multipart_request:
                    # TODO: Why do I have to do this?
                    if 'headers' in http_request.kwargs:
                        http_request.kwargs['headers'].pop(
                            'content-type', None)

                result = await self._dispatch_async(http_request)
        except Exception as e:
            raise HTTPErrorWrapper(typing.cast(types.HTTPErrors, e))

        return http_request.handle_response(result)

    def call(self, func: typing.Callable[..., typing.Any], *args: typing.Any,
             **kwargs: typing.Any) -> typing.Any:
        """Execute the API HTTP request."""
        http_request = HttpRequest(func, self.path_template, args, kwargs)

        try:
            if http_request.rest_client.backend_ == 'httpx' \
                    and http_request.http_method == HttpMethod.GET \
                    and http_request.is_stream:
                del kwargs['stream']

                result = http_request.execution_context.stream(
                    "GET", http_request.req, **http_request.kwargs)
            else:
                if http_request.http_method == HttpMethod.POST \
                        and http_request.is_multipart_request:
                    # TODO: Why do I have to do this?
                    if 'headers' in http_request.kwargs:
                        http_request.kwargs['headers'].pop(
                            'content-type', None)

                result = self._dispatch(http_request)
        except Exception as e:
            raise HTTPErrorWrapper(typing.cast(types.HTTPErrors, e))

        return http_request.handle_response(result)

    def _dispatch(self, http_request: HttpRequest) -> typing.Any:
        """
        Dispatch HTTP method based on HTTPMethod enum type.

        Args:
            execution_context: requests or httpx object
            http_method(HttpMethod): HTTP method
            kwargs(dict): named arguments passed to the API method
            req(): request object
        """
        method = str(http_request.http_method).lower()

        ctx = http_request.execution_context

        return methodcaller(method, http_request.req,
                            **http_request.kwargs)(ctx)

    async def _dispatch_async(self, http_request: HttpRequest) -> typing.Any:
        """
        Dispatch HTTP method based on HTTPMethod enum type.

        Args:
            execution_context: requests or httpx object
            http_method(HttpMethod): HTTP method
            kwargs(dict): named arguments passed to the API method
            req(): request object
        """
        if isinstance(http_request.http_method, str):
            method = http_request.http_method
        else:
            method = http_request.http_method.value[0].lower()

        import httpx

        if not isinstance(http_request.execution_context, httpx.AsyncClient):
            custom_kwargs = dict()
            if http_request.rest_client.auth_() is not None:
                custom_kwargs['auth'] = http_request.rest_client.auth_()
            async with httpx.AsyncClient(**custom_kwargs) as client:
                return await client.request(method.upper(), http_request.req,
                                            **http_request.kwargs)
        else:
            return await http_request.execution_context.request(
                method.upper(), http_request.req, **http_request.kwargs)
