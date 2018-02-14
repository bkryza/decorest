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
"""Decorators implementation.

Each RestClient subclass has a `__decorest__` property storing
a dictionary with decorator values provided by decorators
added to the client class or method.
"""

import inspect
import json
import logging as LOG
import numbers

import requests
from requests.auth import AuthBase
from requests.structures import CaseInsensitiveDict

from six import iteritems

from .client import HttpMethod, HttpStatus, render_path
from .utils import dict_from_args, merge_dicts


DECOR_KEY = '__decorest__'


def set_decor(t, name, value):
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


def get_decor(t, name):
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


DECOR_LIST = ['on', 'query', 'header', 'endpoint', 'content', 'accept', 'body',
              'auth', 'timeout']


def on(status, handler):
    """
    On status result handlers decorator.

    The handler is a function or lambda which will receive as
    the sole parameter the requests response object.
    """
    def on_decorator(t):
        set_decor(t, 'on', {status: handler})
        return t
    return on_decorator


def query(name, value=None):
    """Query parameter decorator."""
    def query_decorator(t):
        value_ = value
        if inspect.isclass(t):
            raise "@query decorator can only be "\
                  "applied to methods."
        if not value_:
            value_ = name
        set_decor(t, 'query', {name: value_})
        return t
    return query_decorator


def header(name, value):
    """Header class and method decorator."""
    def header_decorator(t):
        set_decor(t, 'header', CaseInsensitiveDict({name: value}))
        return t
    return header_decorator


def endpoint(value):
    """Endpoint class and method decorator."""
    def endpoint_decorator(t):
        set_decor(t, 'endpoint', value)
        return t
    return endpoint_decorator


def content(value):
    """Content-type header class and method decorator."""
    def content_decorator(t):
        set_decor(t, 'header', CaseInsensitiveDict({'Content-Type': value}))
        return t
    return content_decorator


def accept(value):
    """Accept header class and method decorator."""
    def accept_decorator(t):
        set_decor(t, 'header', CaseInsensitiveDict({'Accept': value}))
        return t
    return accept_decorator


def body(name, serializer=None):
    """
    Body parameter decorator.

    Determines which method argument provides the body.
    """
    def body_decorator(t):
        set_decor(t, 'body', (name, serializer))
        return t
    return body_decorator


def auth(value):
    """Add authentication method."""
    def auth_decorator(t):
        if not isinstance(value, AuthBase):
            raise "@auth decorator accepts only subclasses " \
                "of 'requests.auth.AuthBase'"
        set_decor(t, 'auth', value)
        return t
    return auth_decorator


def timeout(value):
    """
    Timeout parameter decorator.

    Specifies a default timeout value for method or entire API.
    """
    def timeout_decorator(t):
        set_decor(t, 'timeout', value)
        return t
    return timeout_decorator


def stream(t):
    """
    Stream parameter decorator, takes boolean True or False.

    If specified, adds `stream=value` to requests and the value returned
    from such method will be the requests object.
    """
    set_decor(t, 'stream', True)
    return t


class HttpMethodDecorator(object):
    """Abstract decorator for HTTP method decorators."""

    def __init__(self, path):
        """Initialize decorator with endpoint relative path."""
        self.path_template = path

    def call(self, func, *args, **kwargs):
        """Execute the API HTTP request."""
        http_method = get_decor(func, 'http_method')
        rest_client = args[0]
        args_dict = dict_from_args(func, *args)
        req_path = render_path(self.path_template, args_dict)
        stream = False

        # Merge query parameters from common values for all method
        # invocations with query arguments provided in the method
        # arguments
        query_parameters_decor = get_decor(func, 'query')
        query_parameters = {}
        if query_parameters_decor:
            for query_arg, query_param in iteritems(query_parameters_decor):
                if args_dict.get(query_arg):
                    query_value = args_dict[query_arg]
                    query_parameters[query_param] = query_value

        header_parameters = merge_dicts(
            get_decor(rest_client.__class__, 'header'),
            get_decor(func, 'header'))

        # Get body content from positional arguments if one is specified
        # using @body decorator
        body_parameter = get_decor(func, 'body')
        body_content = None
        if body_parameter:
            LOG.debug("BODY PARAM NAME: " + body_parameter[0])
            body_content = args_dict.get(body_parameter[0])
            LOG.debug("REQUEST BODY: {body}".format(body=str(body_content)))
            # Serialize body content first if serialization handler
            # was provided
            if body_content and body_parameter[1]:
                body_content = body_parameter[1](body_content)
            LOG.debug("SERIALIZED BODY: {body}".format(body=body_content))

        # Get authentication method for this call
        auth = get_decor(func, 'auth')
        if auth is None:
            auth = get_decor(rest_client.__class__, 'auth')

        # Get status handlers
        on_handlers = merge_dicts(
            get_decor(rest_client.__class__, 'on'), get_decor(func, 'on'))

        # Get timeout
        timeout = get_decor(rest_client.__class__, 'timeout')
        if get_decor(func, 'timeout'):
            timeout = get_decor(func, 'timeout')

        # Check if stream is requested for this call
        stream = get_decor(func, 'stream')
        if stream is None:
            stream = get_decor(rest_client.__class__, 'stream')

        #
        # If the kwargs contains any decorest decorators that should
        # be overloaded for this call, extract them.
        #
        # Pass the rest of kwargs to requests calls
        #
        if kwargs:
            for decor in DECOR_LIST:
                if decor in kwargs:
                    if decor == 'header':
                        if not isinstance(kwargs['header'], dict):
                            raise TypeError(
                                "'header' value must be an instance of dict")
                        header_parameters = merge_dicts(
                            header_parameters, kwargs['header'])
                        del kwargs['header']
                    elif decor == 'query':
                        if not isinstance(kwargs['query'], dict):
                            raise TypeError(
                                "'query' value must be an instance of dict")
                        query_parameters = merge_dicts(
                            query_parameters, kwargs['query'])
                        del kwargs['query']
                    elif decor == 'on':
                        if not isinstance(kwargs['on'], dict):
                            raise TypeError(
                                "'on' value must be an instance of dict")
                        on_handlers = merge_dicts(on_handlers, kwargs['on'])
                        del kwargs['on']
                    elif decor == 'accept':
                        if not isinstance(kwargs['accept'], str):
                            raise TypeError(
                                "'accept' value must be an instance of str")
                        header_parameters['accept'] = kwargs['accept']
                        del kwargs['accept']
                    elif decor == 'content':
                        if not isinstance(kwargs['content'], str):
                            raise TypeError(
                                "'content' value must be an instance of str")
                        header_parameters['content-type'] = kwargs['content']
                        del kwargs['content']
                    elif decor == 'auth':
                        if not isinstance(kwargs['auth'], AuthBase):
                            raise TypeError(
                                "'auth' value must be an instance of AuthBase")
                        auth = kwargs['auth']
                        del kwargs['auth']
                    elif decor == 'timeout':
                        if not isinstance(kwargs['timeout'], numbers.Number):
                            raise TypeError(
                                "'timeout' value must be a number")
                        timeout = kwargs['timeout']
                        del kwargs['timeout']
                    elif decor == 'stream':
                        if not isinstance(kwargs['stream'], bool):
                            raise TypeError("'stream' value must be a bool")
                        stream = kwargs['stream']
                        del kwargs['stream']
                    elif decor == 'body':
                        body_content = kwargs['body']
                        del kwargs['body']
                    else:
                        pass

        # Build request from endpoint and query params
        if get_decor(rest_client.__class__, 'endpoint'):
            rest_client.endpoint = get_decor(rest_client.__class__, 'endpoint')

        req = rest_client.build_request(req_path.split('/'))

        # Assume default content type
        if 'content-type' not in header_parameters:
            header_parameters['content-type'] = 'application/json'

        # Assume default accept
        if 'accept' not in header_parameters:
            header_parameters['accept'] = 'application/json'

        LOG.debug('REQUEST: {method} {request}'.format(
            method=http_method, request=req))

        if auth:
            kwargs['auth'] = auth
        if timeout:
            kwargs['timeout'] = timeout
        if body_content:
            if header_parameters.get('content-type') == 'application/json':
                if isinstance(body_content, dict):
                    kwargs['data'] = json.dumps(body_content)
                else:
                    kwargs['data'] = body_content
            else:
                kwargs['data'] = body_content
            LOG.debug("BODY TYPE: " + str(type(kwargs['data'])))
        if header_parameters:
            kwargs['headers'] = header_parameters
            LOG.debug("CONTENT_TYPE " + header_parameters['content-type'])
        if query_parameters:
            kwargs['params'] = query_parameters
        if stream:
            kwargs['stream'] = stream

        result = None

        if http_method == HttpMethod.GET:
            result = requests.get(req, **kwargs)
        elif http_method == HttpMethod.POST:
            result = requests.post(req, **kwargs)
        elif http_method == HttpMethod.PUT:
            result = requests.put(req, **kwargs)
        elif http_method == HttpMethod.PATCH:
            result = requests.patch(req, **kwargs)
        elif http_method == HttpMethod.DELETE:
            result = requests.delete(req, **kwargs)
        elif http_method == HttpMethod.HEAD:
            result = requests.head(req, **kwargs)
        elif http_method == HttpMethod.OPTIONS:
            result = requests.options(req, **kwargs)
        else:
            raise 'Unsupported HTTP method: {method}'.format(
                method=http_method)

        if on_handlers and result.status_code in on_handlers:
            # Use a registered handler for the returned status code
            return on_handlers[result.status_code](result)
        elif on_handlers and HttpStatus.ANY in on_handlers:
            # If a catch all status handler is provided - use it
            return on_handlers[HttpStatus.ANY](result)
        else:
            # If stream option was passed and no content handler
            # was defined, return requests response
            if stream:
                return result

            # Default response handler
            result.raise_for_status()

            if result.text:
                content_type = result.headers.get('content-type')
                if content_type == 'application/json':
                    return result.json()
                elif content_type == 'application/octet-stream':
                    return result.content
                else:
                    return result.text

            return None
