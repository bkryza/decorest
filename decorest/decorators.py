import logging as LOG
import requests
import inspect
from functools import wraps

from .client import RestClient, HttpMethod, render_path
from .utils import merge_dicts, dict_from_args


"""
Each RestClient subclass has a `_decors` property storing
a dictionary with decorator values provided by decorators
added to the client class.
"""


def set_decor(t, name, value):
    """
    Decorates a function or class by storing the value under specific
    path.
    """
    if not hasattr(t, '_decors'):
        t._decors = {}

    if isinstance(value, dict):
        if not t._decors.get(name):
            t._decors[name] = {}
        t._decors[name] = merge_dicts(t._decors[name], value)
    elif isinstance(value, list):
        if not t._decors.get(name):
            t._decors[name] = []
        t._decors[name].extend(value)
    else:
        t._decors[name] = value


def get_decor(t, name):
    """
    Retrieves a named decorator value from class or function.
    """
    if hasattr(t, '_decors') and t._decors.get(name):
        return t._decors[name]

    return None


def on(status, handler):
    """
    On status result handlers decorator

    The handler is a function or lambda which will receive as
    the sole parameter the requests response object.
    """
    def on_decorator(t):
        set_decor(t, 'on', {status: handler})
        return t
    return on_decorator


def query(name, value=None):
    """
    Query parameter decorator
    """
    def query_decorator(f):
        set_decor(t, 'query', {name: value})
        return f
    return query_decorator


def header(name, value):
    """
    Header class and method decorator
    """
    def header_decorator(t):
        set_decor(t, 'header', {name: value})
        return t
    return header_decorator


def body(name):
    """
    Body parameter decorator.

    Determines which method argument provides the body.
    """
    def body_decorator(t):
        set_decor(t, 'body', name)
        return t
    return body_decorator


def auth(value):
    """
    Authentication decorator
    """
    def auth_decorator(t):
        if not isinstance(value, requests.auth.AuthBase):
            raise "@auth decorator accepts only subclasses " \
                "of 'requests.auth.AuthBase'"
        set_decor(t, 'auth', value)
        return t
    return auth_decorator


class HttpMethodDecorator(object):
    """
    Abstract decorator for HTTP method decorators
    """

    def __init__(self, path):
        self.path_template = path

    def call(self, func, *args, **kwargs):
        http_method = func._http__method
        rest_client = args[0]
        args_dict = dict_from_args(func, *args)
        req_path = render_path(self.path_template, args_dict)

        query_parameters = get_decor(func, 'query')
        header_parameters = merge_dicts(
            get_decor(rest_client.__class__, 'header'),
            get_decor(func, 'header'))

        # Get body content from named arguments
        body_parameter = get_decor(func, 'body')
        body_content = args_dict.get(body_parameter)
        LOG.debug("REQUEST BODY: {body}".format(body=body_content))

        # Get authentication method for this call
        auth = get_decor(func, 'auth')
        if auth is None:
            auth = get_decor(rest_client.__class__, 'auth')

        # Get status handlers
        on_handlers = merge_dicts(
            get_decor(rest_client.__class__, 'on'), get_decor(func, 'on'))

        # Build request from endpoint and query params
        req = rest_client.build_request(
            req_path.split('/'), query_parameters)

        # Assume default content type
        if 'content-type' not in header_parameters:
            header_parameters['content-type'] = 'application/json'

        # Assume default accept
        if 'accept' not in header_parameters:
            header_parameters['accept'] = 'application/json'

        LOG.debug('REQUEST: {method} {request}'.format(
            method=http_method, request=req))

        result = None

        if http_method == HttpMethod.GET:
            result = requests.get(req, auth=auth,
                                  headers=header_parameters, data=body_content)
        elif http_method == HttpMethod.POST:
            result = requests.post(req, auth=auth,
                                   headers=header_parameters, data=body_content)
        elif http_method == HttpMethod.PUT:
            result = requests.put(req, auth=auth,
                                  headers=header_parameters, data=body_content)
        elif http_method == HttpMethod.DELETE:
            result = requests.delete(req, auth=auth,
                                     headers=header_parameters, data=body_content)
        elif http_method == HttpMethod.UPDATE:
            result = requests.update(req, auth=auth,
                                     headers=header_parameters, data=body_content)
        elif http_method == HttpMethod.HEAD:
            result = requests.head(req, auth=auth,
                                   headers=header_parameters, data=body_content)
        else:
            raise 'Unsupported HTTP method: {method}'.format(
                method=http_method)

        if result.status_code in on_handlers:
            # Use a registered handler for the returned status code
            return on_handlers[result.status_code](result)
        else:
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
