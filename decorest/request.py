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
"""HTTP request wrapper."""
import json
import logging as LOG
import numbers
import typing

from .client import RestClient
from .decorator_utils import DECOR_LIST, get_body_decor, get_decor, \
    get_header_decor, get_method_class_decor, get_method_decor, \
    get_on_decor, get_stream_decor, get_timeout_decor
from .errors import HTTPErrorWrapper
from .types import ArgsDict, HTTPErrors, HttpMethod, HttpStatus
from .utils import CaseInsensitiveDict
from .utils import dict_from_args, merge_dicts, render_path


class HttpRequest:
    """
    HTTP request wrapper.

    Class representing an HTTP request created from decorators and arguments.
    """
    http_method: HttpMethod
    is_multipart_request: bool
    is_stream: bool
    req: str
    kwargs: ArgsDict
    on_handlers: typing.Mapping[int, typing.Callable[..., typing.Any]]
    session: typing.Optional[str]
    session_endpoint: typing.Optional[str]
    execution_context: typing.Any
    rest_client: RestClient

    def __init__(self, func: typing.Callable[...,
                                             typing.Any], path_template: str,
                 args: typing.Tuple[typing.Any, ...], kwargs: ArgsDict):
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
            raise ValueError('Unsupported HTTP method: {method}'.format(
                method=self.http_method))

        self.rest_client = args[0]

        args_dict = dict_from_args(func, *args)
        self.req_path = render_path(self.path_template, args_dict)
        self.session = None
        if '__session' in self.kwargs:
            self.session = self.kwargs['__session']
            del self.kwargs['__session']
        self.session_endpoint = None
        if '__endpoint' in self.kwargs:
            self.session_endpoint = self.kwargs['__endpoint']
            del self.kwargs['__endpoint']

        # Merge query parameters from common values for all method
        # invocations with arguments provided in the method
        # arguments
        query_parameters = self._merge_args(args_dict, func, 'query')
        form_parameters = self._merge_args(args_dict, func, 'form')
        multipart_parameters = self._merge_args(args_dict, func, 'multipart')
        header_parameters = CaseInsensitiveDict(
            merge_dicts(get_header_decor(self.rest_client.__class__),
                        self._merge_args(args_dict, func, 'header')))

        # Merge header parameters with default values, treat header
        # decorators with 2 params as default values only if they
        # don't match the function argument names
        func_header_decors = get_header_decor(func)

        if func_header_decors:
            for key, value in func_header_decors.items():
                if key not in args_dict:
                    header_parameters[key] = value

        for key, value in header_parameters.items():
            if isinstance(value, list):
                header_parameters[key] = ", ".join(value)

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
        auth = self.rest_client.auth_()

        # Get status handlers
        self.on_handlers = merge_dicts(
            get_on_decor(self.rest_client.__class__), get_on_decor(func))

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
                        self._validate_decor(decor, self.kwargs, dict)
                        header_parameters \
                            = typing.cast(CaseInsensitiveDict, merge_dicts(
                                header_parameters, self.kwargs['header']))
                        del self.kwargs['header']
                    elif decor == 'query':
                        self._validate_decor(decor, self.kwargs, dict)
                        query_parameters = merge_dicts(query_parameters,
                                                       self.kwargs['query'])
                        del self.kwargs['query']
                    elif decor == 'form':
                        self._validate_decor(decor, self.kwargs, dict)
                        form_parameters = merge_dicts(form_parameters,
                                                      self.kwargs['form'])
                        del self.kwargs['form']
                    elif decor == 'multipart':
                        self._validate_decor(decor, self.kwargs, dict)
                        multipart_parameters = merge_dicts(
                            multipart_parameters, self.kwargs['multipart'])
                        del self.kwargs['multipart']
                    elif decor == 'on':
                        self._validate_decor(decor, self.kwargs, dict)
                        self.on_handlers = merge_dicts(self.on_handlers,
                                                       self.kwargs['on'])
                        del self.kwargs['on']
                    elif decor == 'accept':
                        self._validate_decor(decor, self.kwargs, str)
                        header_parameters['accept'] = self.kwargs['accept']
                        del self.kwargs['accept']
                    elif decor == 'content':
                        self._validate_decor(decor, self.kwargs, str)
                        header_parameters['content-type'] \
                            = self.kwargs['content']
                        del self.kwargs['content']
                    elif decor == 'timeout':
                        self._validate_decor(decor, self.kwargs,
                                             numbers.Number)
                        request_timeout = self.kwargs['timeout']
                        del self.kwargs['timeout']
                    elif decor == 'stream':
                        self._validate_decor(decor, self.kwargs, bool)
                        self.is_stream = self.kwargs['stream']
                        del self.kwargs['stream']
                    elif decor == 'body':
                        body_content = self.kwargs['body']
                        del self.kwargs['body']
                    else:
                        pass

        # Build request from endpoint and query params
        effective_endpoint = self.session_endpoint \
            or self.rest_client.endpoint_ \
            or get_method_class_decor(func, self.rest_client, 'endpoint')\
            or get_decor(self.rest_client, 'endpoint')

        self.req = self.rest_client.build_path_(self.req_path.split('/'),
                                                effective_endpoint)

        # Handle multipart parameters, either from decorators
        # or ones passed directly through kwargs
        if multipart_parameters:
            self.is_multipart_request = True
            self.kwargs['files'] = multipart_parameters
        elif self.rest_client.backend_ == 'requests':
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

        # If '__session' was passed in the kwargs, execute this request
        # using the session context, otherwise execute directly via the
        # requests or httpx module
        if self.session:
            self.execution_context = self.session
        else:
            if self.rest_client.backend_ == 'requests':
                import requests
                self.execution_context = requests
            else:
                import httpx
                self.execution_context = httpx

        if auth:
            self.kwargs['auth'] = auth

        if request_timeout:
            self.kwargs['timeout'] = request_timeout
        if body_content:
            if header_parameters.get('content-type') == 'application/json':
                if isinstance(body_content, dict):
                    body_content = json.dumps(body_content)

            if self.rest_client.backend_ == 'httpx':
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

        try:
            import httpx
            if isinstance(self.execution_context,
                          (httpx.Client, httpx.AsyncClient)):
                # httpx does not allow 'auth' parameter on session requests
                if 'auth' in self.kwargs:
                    del self.kwargs['auth']
                if 'follow_redirects' not in self.kwargs:
                    self.kwargs['follow_redirects'] = True

                merge_dicts(self.kwargs, self.rest_client.client_args_)

            if self.execution_context is httpx:
                if 'follow_redirects' not in self.kwargs:
                    self.kwargs['follow_redirects'] = True
        except ImportError:
            pass

        if self.rest_client.backend_ == 'requests':
            self._normalize_for_requests(self.kwargs)
        else:
            self._normalize_for_httpx(self.kwargs)

    def __repr__(self) -> str:
        """Return instance representation."""
        return f'<{type(self).__name__} method: {str(self.http_method)} ' \
               f'path: \'{self.req_path}\'>'

    def _normalize_for_httpx(self, kwargs: ArgsDict) -> None:
        """
        Normalize kwargs for httpx.

        Translates and converts argument names and values from
        requests to httpx, e.g.
            'allow_redirects' -> 'follow_redirects'
        """
        if 'allow_redirects' in kwargs:
            kwargs['follow_redirects'] = kwargs['allow_redirects']
            del kwargs['allow_redirects']

    def _normalize_for_requests(self, kwargs: ArgsDict) -> None:
        """
        Normalize kwargs for requests.

        Translates and converts argument names and values from
        requests to httpx, e.g.
            'follow_redirects' -> 'allow_redirects'
        """
        if 'follow_redirects' in kwargs:
            kwargs['allow_redirects'] = kwargs['follow_redirects']
            del kwargs['follow_redirects']

    def handle_response(self, result: typing.Any) -> typing.Any:
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
                raise HTTPErrorWrapper(typing.cast(HTTPErrors, e))

            if result.text:
                content_type = result.headers.get('content-type')
                if content_type == 'application/json':
                    return result.json()
                elif content_type == 'application/octet-stream':
                    return result.content
                else:
                    return result.text

            return None

    def _validate_decor(self, decor: str, kwargs: ArgsDict,
                        cls: typing.Type[typing.Any]) -> None:
        """
        Ensure kwargs contain decor with specific type.

        Args:
            decor(str): Name of the decorator
            kwargs(dict): Named arguments passed to API call
            cls(class): Expected type of decorator parameter
        """
        if not isinstance(kwargs[decor], cls):
            raise TypeError("{} value must be an instance of {}".format(
                decor, cls.__name__))

    def _merge_args(self, args_dict: ArgsDict,
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
            for arg, value in args_decor.items():
                if (isinstance(value, str)) \
                        and arg in args_dict.keys():
                    parameters[value] = args_dict[arg]
                else:
                    parameters[arg] = value
        return parameters
