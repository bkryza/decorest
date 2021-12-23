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
"""Decorators implementation.

Each RestClient subclass has a `__decorest__` property storing
a dictionary with decorator values provided by decorators
added to the client class or method.
"""

import inspect
import json
import logging as LOG
import numbers
import pprint
import typing
from operator import methodcaller

import requests
from requests.structures import CaseInsensitiveDict

from . import types
from .errors import HTTPErrorWrapper
from .types import ArgsDict, HttpMethod, HttpStatus, TDecor
from .utils import dict_from_args, merge_dicts, render_path

DECOR_KEY = '__decorest__'

DECOR_LIST = [
    'header', 'query', 'form', 'multipart', 'on', 'accept', 'content',
    'timeout', 'stream', 'body', 'endpoint'
]


def set_decor(t: typing.Any, name: str, value: typing.Any) -> None:
    """Decorate a function or class by storing the value under specific key."""
    if hasattr(t, '__wrapped__') and hasattr(t.__wrapped__, DECOR_KEY):
        setattr(t, DECOR_KEY, t.__wrapped__.__decorest__)

    if not hasattr(t, DECOR_KEY):
        setattr(t, DECOR_KEY, {})

    d = getattr(t, DECOR_KEY)

    if isinstance(value, CaseInsensitiveDict):
        if not d.get(name):
            d[name] = CaseInsensitiveDict()
        d[name] = merge_dicts(d[name], value)
    elif isinstance(value, dict):
        if not d.get(name):
            d[name] = {}
        d[name] = merge_dicts(d[name], value)
    elif isinstance(value, list):
        if not d.get(name):
            d[name] = []
        d[name].extend(value)
    else:
        d[name] = value


def get_decor(t: typing.Any, name: str) -> typing.Optional[typing.Any]:
    """
    Retrieve a named decorator value from class or function.

    Args:
        t (type): Decorated type (can be class or function)
        name (str): Name of the key

    Returns:
        object: any value assigned to the name key

    """
    if hasattr(t, DECOR_KEY) and getattr(t, DECOR_KEY).get(name):
        return getattr(t, DECOR_KEY)[name]

    return None


def get_method_decor(t: typing.Any) -> HttpMethod:
    """Return http method decor value."""
    return typing.cast(HttpMethod, get_decor(t, 'http_method'))


def get_header_decor(t: typing.Any) -> typing.Optional[typing.Dict[str, str]]:
    """Return header decor values."""
    return typing.cast(typing.Optional[typing.Dict[str, str]],
                       get_decor(t, 'header'))


def get_query_decor(t: typing.Any) -> typing.Optional[typing.Dict[str, str]]:
    """Return query decor values."""
    return typing.cast(typing.Optional[typing.Dict[str, str]],
                       get_decor(t, 'query'))


def get_form_decor(t: typing.Any) -> typing.Optional[typing.Dict[str, str]]:
    """Return form decor values."""
    return typing.cast(typing.Optional[typing.Dict[str, str]],
                       get_decor(t, 'form'))


def get_multipart_decor(t: typing.Any) \
        -> typing.Optional[typing.Dict[str, str]]:
    """Return multipart decor values."""
    return typing.cast(typing.Optional[typing.Dict[str, str]],
                       get_decor(t, 'multipart'))


def get_on_decor(t: typing.Any) \
        -> typing.Optional[typing.Dict[int, typing.Any]]:
    """Return on decor values."""
    return typing.cast(typing.Optional[typing.Dict[int, typing.Any]],
                       get_decor(t, 'on'))


def get_accept_decor(t: typing.Any) -> typing.Optional[str]:
    """Return accept decor value."""
    return typing.cast(typing.Optional[str],
                       get_decor(t, 'accept'))


def get_content_decor(t: typing.Any) -> typing.Optional[str]:
    """Return content-type decor value."""
    return typing.cast(typing.Optional[str],
                       get_decor(t, 'content'))


def get_timeout_decor(t: typing.Any) -> typing.Optional[numbers.Real]:
    """Return timeout decor value."""
    return typing.cast(typing.Optional[numbers.Real],
                       get_decor(t, 'timeout'))


def get_stream_decor(t: typing.Any) -> bool:
    """Return stream decor value."""
    return typing.cast(bool, get_decor(t, 'stream'))


def get_body_decor(t: typing.Any) -> typing.Optional[typing.Any]:
    """Return body decor value."""
    return get_decor(t, 'body')


def get_endpoint_decor(t: typing.Any) -> typing.Optional[str]:
    """Return endpoint decor value."""
    return typing.cast(typing.Optional[str], get_decor(t, 'endpoint'))


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
            raise TypeError("Status in @on decorator must be integer or '...'")
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
        if not value_:
            value_ = name
        set_decor(t, 'query', {name: value_})
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
        if not value_:
            value_ = name
        set_decor(t, 'form', {name: value_})
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
        if not value_:
            value_ = name
        set_decor(t, 'multipart', {name: value_})
        return t

    return multipart_decorator


def header(name: str, value: typing.Optional[str] = None) \
        -> typing.Callable[[TDecor], TDecor]:
    """Header class and method decorator."""

    def header_decorator(t: TDecor) -> TDecor:
        value_ = value
        if not value_:
            value_ = name
        set_decor(t, 'header', CaseInsensitiveDict({name: value_}))
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
        set_decor(t, 'header',
                  CaseInsensitiveDict({'Content-Type': value}))
        return t

    return content_decorator


def accept(value: str) -> typing.Callable[[TDecor], TDecor]:
    """Accept header class and method decorator."""

    def accept_decorator(t: TDecor) -> TDecor:
        set_decor(t, 'header',
                  CaseInsensitiveDict({'Accept': value}))
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


# return execution_context, on_handlers, rest_client
class HttpRequest:
    """
    HTTP request wrapper.

    Class representing an HTTP request created from decorators and arguments.
    """
    http_method: str
    is_multipart_request: bool
    is_stream: bool
    req: str
    kwargs: ArgsDict
    on_handlers: typing.Mapping[int, typing.Callable[..., typing.Any]]
    session: str
    execution_context: typing.Any
    rest_client: 'RestClient' # noqa

    def __init__(self, func, path_template, args, kwargs):
        """
        Construct HttpRequest instance.

        Args:
            func - decorated function
            path_template - template for creating the request path
            args - arguments
            kwargs - named arguments
        """
        self.http_method = get_method_decor(func)
        self.path_template = path_template
        self.kwargs = kwargs

        if self.http_method not in (HttpMethod.GET, HttpMethod.POST,
                                    HttpMethod.PUT, HttpMethod.PATCH,
                                    HttpMethod.DELETE, HttpMethod.HEAD,
                                    HttpMethod.OPTIONS):
            raise ValueError(
                'Unsupported HTTP method: {method}'.format(
                    method=self.http_method))

        self.rest_client = args[0]
        args_dict = dict_from_args(func, *args)
        req_path = render_path(self.path_template, args_dict)
        self.session = None
        if '__session' in self.kwargs:
            self.session = self.kwargs['__session']
            del self.kwargs['__session']
        # Merge query parameters from common values for all method
        # invocations with arguments provided in the method
        # arguments
        query_parameters = self.__merge_args(args_dict, func, 'query')
        form_parameters = self.__merge_args(args_dict, func, 'form')
        multipart_parameters = self.__merge_args(args_dict, func, 'multipart')
        header_parameters = merge_dicts(
            get_header_decor(self.rest_client.__class__),
            self.__merge_args(args_dict, func, 'header'))
        # Merge header parameters with default values, treat header
        # decorators with 2 params as default values only if they
        # don't match the function argument names
        func_header_decors = get_header_decor(func)
        if func_header_decors:
            for key in func_header_decors.keys():
                if not func_header_decors[key] in args_dict:
                    header_parameters[key] = func_header_decors[key]
        # Get body content from positional arguments if one is specified
        # using @body decorator
        body_parameter = get_body_decor(func)
        body_content = None
        if body_parameter:
            body_content = args_dict.get(body_parameter[0])
            # Serialize body content first if serialization handler
            # was provided
            if body_content and body_parameter[1]:
                body_content = body_parameter[1](body_content)
        # Get authentication method for this call
        auth = self.rest_client._auth()
        # Get status handlers
        self.on_handlers = merge_dicts(get_on_decor(self.rest_client.__class__),
                                       get_on_decor(func))
        # Get timeout
        request_timeout = get_timeout_decor(self.rest_client.__class__)
        if get_timeout_decor(func):
            request_timeout = get_timeout_decor(func)
        # Check if stream is requested for this call
        self.is_stream = get_stream_decor(func)
        if self.is_stream is None:
            self.is_stream = get_stream_decor(self.rest_client.__class__)
        #
        # If the kwargs contains any decorest decorators that should
        # be overloaded for this call, extract them.
        #
        # Pass the rest of kwargs to requests calls
        #
        if self.kwargs:
            for decor in DECOR_LIST:
                if decor in self.kwargs:
                    if decor == 'header':
                        self.__validate_decor(decor, self.kwargs, dict)
                        header_parameters = merge_dicts(
                            header_parameters, self.kwargs['header'])
                        del self.kwargs['header']
                    elif decor == 'query':
                        self.__validate_decor(decor, self.kwargs, dict)
                        query_parameters = merge_dicts(query_parameters,
                                                       self.kwargs['query'])
                        del self.kwargs['query']
                    elif decor == 'form':
                        self.__validate_decor(decor, self.kwargs, dict)
                        form_parameters = merge_dicts(form_parameters,
                                                      self.kwargs['form'])
                        del self.kwargs['form']
                    elif decor == 'multipart':
                        self.__validate_decor(decor, self.kwargs, dict)
                        multipart_parameters = merge_dicts(
                            multipart_parameters, self.kwargs['multipart'])
                        del self.kwargs['multipart']
                    elif decor == 'on':
                        self.__validate_decor(decor, self.kwargs, dict)
                        self.on_handlers = merge_dicts(self.on_handlers,
                                                       self.kwargs['on'])
                        del self.kwargs['on']
                    elif decor == 'accept':
                        self.__validate_decor(decor, self.kwargs, str)
                        header_parameters['accept'] = self.kwargs['accept']
                        del self.kwargs['accept']
                    elif decor == 'content':
                        self.__validate_decor(decor, self.kwargs, str)
                        header_parameters['content-type'] \
                            = self.kwargs['content']
                        del self.kwargs['content']
                    elif decor == 'timeout':
                        self.__validate_decor(decor, self.kwargs,
                                              numbers.Number)
                        request_timeout = self.kwargs['timeout']
                        del self.kwargs['timeout']
                    elif decor == 'stream':
                        self.__validate_decor(decor, self.kwargs, bool)
                        self.is_stream = self.kwargs['stream']
                        del self.kwargs['stream']
                    elif decor == 'body':
                        body_content = self.kwargs['body']
                        del self.kwargs['body']
                    else:
                        pass
        # Build request from endpoint and query params
        self.req = self.rest_client.build_request(req_path.split('/'))

        # Handle multipart parameters, either from decorators
        # or ones passed directly through kwargs
        if multipart_parameters:
            self.is_multipart_request = True
            self.kwargs['files'] = multipart_parameters
        elif self.rest_client._backend() == 'requests':
            from requests_toolbelt.multipart.encoder import MultipartEncoder
            self.is_multipart_request = \
                'data' in self.kwargs and \
                not isinstance(self.kwargs['data'], MultipartEncoder)
        else:
            self.is_multipart_request = 'files' in self.kwargs

        # Assume default content type if not multipart
        if ('content-type' not in header_parameters) \
                and not self.is_multipart_request:
            header_parameters['content-type'] = 'application/json'

        # Assume default accept
        if 'accept' not in header_parameters:
            header_parameters['accept'] = 'application/json'

        LOG.debug('Request: {method} {request}'.format(method=self.http_method,
                                                       request=self.req))
        if auth:
            self.kwargs['auth'] = auth
        if request_timeout:
            self.kwargs['timeout'] = request_timeout
        if body_content:
            if header_parameters.get('content-type') == 'application/json':
                if isinstance(body_content, dict):
                    body_content = json.dumps(body_content)

            if self.rest_client._backend() == 'httpx':
                if isinstance(body_content, dict):
                    self.kwargs['data'] = body_content
                else:
                    self.kwargs['content'] = body_content
            else:
                kwargs['data'] = body_content
        if query_parameters:
            self.kwargs['params'] = query_parameters
        if form_parameters:
            # If form parameters were passed, override the content-type
            header_parameters['content-type'] \
                = 'application/x-www-form-urlencoded'
            self.kwargs['data'] = form_parameters
        if self.is_stream:
            self.kwargs['stream'] = self.is_stream
        if header_parameters:
            self.kwargs['headers'] = dict(header_parameters.items())

        # If '__session' was passed in the kwargs, execute this request
        # using the session context, otherwise execute directly via the
        # requests or httpx module
        if self.session:
            self.execution_context = self.session
        else:
            if self.rest_client._backend() == 'requests':
                self.execution_context = requests
            else:
                import httpx
                self.execution_context = httpx

    def __validate_decor(self, decor: str, kwargs: ArgsDict,
                         cls: typing.Type[typing.Any]) -> None:
        """
        Ensure kwargs contain decor with specific type.

        Args:
            decor(str): Name of the decorator
            kwargs(dict): Named arguments passed to API call
            cls(class): Expected type of decorator parameter
        """
        if not isinstance(kwargs[decor], cls):
            raise TypeError(
                "{} value must be an instance of {}".format(
                    decor, cls.__name__))

    def __merge_args(self, args_dict: ArgsDict,
                     func: typing.Callable[..., typing.Any], decor: str) \
            -> ArgsDict:
        """
        Match named arguments from method call.

        Args:
            args_dict (dict): Function arguments dictionary
            func (type): Decorated function
            decor (str): Name of specific decorator (e.g. 'query')

        Returns:
            object: any value assigned to the name key
        """
        args_decor = get_decor(func, decor)
        parameters = {}
        if args_decor:
            for arg, param in args_decor.items():
                if args_dict.get(arg):
                    parameters[param] = args_dict[arg]
        return parameters

    def handle(self, result):
        """Handle result response."""
        if self.on_handlers and result.status_code in self.on_handlers:
            # Use a registered handler for the returned status code
            return self.on_handlers[result.status_code](result)
        elif self.on_handlers and HttpStatus.ANY in self.on_handlers:
            # If a catch all status handler is provided - use it
            return self.on_handlers[HttpStatus.ANY](result)
        else:
            # If stream option was passed and no content handler
            # was defined, return response
            if self.is_stream:
                return result

            # Default response handler
            try:
                result.raise_for_status()
            except Exception as e:
                raise HTTPErrorWrapper(typing.cast(types.HTTPErrors, e))

            if result.text:
                content_type = result.headers.get('content-type')
                if content_type == 'application/json':
                    return result.json()
                elif content_type == 'application/octet-stream':
                    return result.content
                else:
                    return result.text

            return None


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
            pprint.pprint(http_request)
            if http_request.http_method == HttpMethod.GET \
                    and http_request.is_stream:
                del kwargs['stream']
                req = http_request.execution_context.build_request(
                    'GET', http_request.req, **http_request.kwargs)

                result = await http_request.execution_context.send(req,
                                                                   stream=True)
            else:
                if http_request.http_method == HttpMethod.POST \
                        and http_request.is_multipart_request:
                    # TODO: Why do I have to do this?
                    if 'headers' in http_request.kwargs:
                        http_request.kwargs['headers'].pop('content-type', None)

                result = await self.__dispatch_async(http_request)
        except Exception as e:
            raise HTTPErrorWrapper(typing.cast(types.HTTPErrors, e))

        return http_request.handle(result)

    def call(self, func: typing.Callable[..., typing.Any],
             *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        """Execute the API HTTP request."""
        http_request = HttpRequest(func, self.path_template, args, kwargs)

        try:
            if http_request.rest_client._backend() == 'httpx' \
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
                        http_request.kwargs['headers'].pop('content-type', None)

                result = self.__dispatch(http_request)
        except Exception as e:
            raise HTTPErrorWrapper(typing.cast(types.HTTPErrors, e))

        return http_request.handle(result)

    def __dispatch(self, http_request: HttpRequest) -> typing.Any:
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

        ctx = http_request.execution_context
        return methodcaller(method,
                            http_request.req,
                            **http_request.kwargs)(ctx)

    async def __dispatch_async(self, http_request: HttpRequest) -> typing.Any:
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
            async with httpx.AsyncClient() as client:
                return await client.request(method.upper(),
                                            http_request.req,
                                            **http_request.kwargs)
        else:
            return await http_request.execution_context.request(
                method.upper(), http_request.req, **http_request.kwargs)
