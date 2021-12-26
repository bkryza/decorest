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
"""Decorator utility functions."""

import numbers
import typing

from requests.structures import CaseInsensitiveDict

from .types import HeaderDict, HttpMethod
from .utils import merge_dicts, merge_header_dicts

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


def set_header_decor(t: typing.Any, value: HeaderDict) -> None:
    """Decorate a function or class with header decorator."""
    if hasattr(t, '__wrapped__') and hasattr(t.__wrapped__, DECOR_KEY):
        setattr(t, DECOR_KEY, t.__wrapped__.__decorest__)

    if not hasattr(t, DECOR_KEY):
        setattr(t, DECOR_KEY, {})

    d = getattr(t, DECOR_KEY)
    name = 'header'

    if not d.get(name):
        d[name] = CaseInsensitiveDict()

    d[name] = merge_header_dicts(d[name], value)


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
    return typing.cast(typing.Optional[str], get_decor(t, 'accept'))


def get_content_decor(t: typing.Any) -> typing.Optional[str]:
    """Return content-type decor value."""
    return typing.cast(typing.Optional[str], get_decor(t, 'content'))


def get_timeout_decor(t: typing.Any) -> typing.Optional[numbers.Real]:
    """Return timeout decor value."""
    return typing.cast(typing.Optional[numbers.Real], get_decor(t, 'timeout'))


def get_stream_decor(t: typing.Any) -> bool:
    """Return stream decor value."""
    return typing.cast(bool, get_decor(t, 'stream'))


def get_body_decor(t: typing.Any) -> typing.Optional[typing.Any]:
    """Return body decor value."""
    return get_decor(t, 'body')


def get_endpoint_decor(t: typing.Any) -> typing.Optional[str]:
    """Return endpoint decor value."""
    return typing.cast(typing.Optional[str], get_decor(t, 'endpoint'))
