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
"""Decorator utility functions."""
import inspect
import numbers
import typing

from .types import Backends, HeaderDict, HttpMethod
from .utils import CaseInsensitiveDict, merge_dicts, merge_header_dicts

DECOR_KEY = '__decorest__'

DECOR_LIST = [
    'header', 'query', 'form', 'multipart', 'on', 'accept', 'content',
    'timeout', 'stream', 'body', 'endpoint', 'backend'
]


def decor_key_cls(cls: type) -> str:
    """Get class specific decor key."""
    assert (inspect.isclass(cls))
    return DECOR_KEY + cls.__name__


def set_decor_value(d: typing.MutableMapping[str, typing.Any], name: str,
                    value: typing.Any) -> None:
    """Set decorator value in the decorator dict."""
    if isinstance(value, dict):
        if not d.get(name):
            d[name] = {}
        d[name] = merge_dicts(d[name], value)
    elif isinstance(value, list):
        if not d.get(name):
            d[name] = []
        d[name].extend(value)
    else:
        d[name] = value


def set_decor(t: typing.Any, name: str, value: typing.Any) -> None:
    """Decorate a function or class by storing the value under specific key."""
    if hasattr(t, '__wrapped__') and hasattr(t.__wrapped__, DECOR_KEY):
        setattr(t, DECOR_KEY, t.__wrapped__.__decorest__)

    if not hasattr(t, DECOR_KEY):
        setattr(t, DECOR_KEY, {})

    # Set the decor value in the common decorator
    set_decor_value(getattr(t, DECOR_KEY), name, value)

    # Set the decor value in the class specific decorator
    # for reverse inheritance of class decors
    if inspect.isclass(t):
        if not hasattr(t, decor_key_cls(t)):
            setattr(t, decor_key_cls(t), {})
        set_decor_value(getattr(t, decor_key_cls(t)), name, value)


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


def get_class_specific_decor(t: typing.Any,
                             name: str) -> typing.Optional[typing.Any]:
    """
    Retrieve a named decorator value from specific class.

    Args:
        t (type): Decorated class
        name (str): Name of the key

    Returns:
        object: any value assigned to the name key

    """
    if inspect.isclass(t):
        class_decor_key = DECOR_KEY + t.__name__
        if hasattr(t, class_decor_key) and name in getattr(t, class_decor_key):
            return getattr(t, class_decor_key)[name]

    return None


def get_decor(t: typing.Any, name: str) -> typing.Optional[typing.Any]:
    """
    Retrieve a named decorator value from class or function.

    Args:
        t (type): Decorated type (can be class or function)
        name (str): Name of the key

    Returns:
        object: any value assigned to the name key

    """
    class_specific_decor = get_class_specific_decor(t, name)
    if class_specific_decor:
        return class_specific_decor

    if hasattr(t, DECOR_KEY) and name in getattr(t, DECOR_KEY):
        return getattr(t, DECOR_KEY)[name]

    return None


def get_method_class_decor(f: typing.Any, c: typing.Any, name: str) \
        -> typing.Any:
    """Get decorator from base class of c where method f is defined."""
    decor = None
    # First find all super classes which 'have' method f
    # (this will not work in case of name conflicts)
    classes_with_f = []
    for base_class in inspect.getmro(c.__class__):
        decor = get_decor(base_class, name)
        for m in inspect.getmembers(base_class, predicate=inspect.isfunction):
            if m[0] == f.__name__:
                classes_with_f.append(base_class)
                break

    # Now sort the classes based on the inheritance chain
    def sort_by_superclass(a: typing.Any, b: typing.Any) -> int:
        """Compare two types according to inheritance relation."""
        if a == b:
            return 0
        elif issubclass(b, a):
            return -1
        else:
            return 1

    import functools
    classes_with_f.sort(key=functools.cmp_to_key(sort_by_superclass))

    # Now get the decor from the first class in the list which has
    # the requested decor
    for base in classes_with_f:
        decor = get_class_specific_decor(base, name)
        if decor:
            break

    return decor


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
    header_decor = get_header_decor(t)
    if not header_decor:
        return None

    if 'accept' in header_decor:
        return header_decor['accept']

    return None


def get_content_decor(t: typing.Any) -> typing.Optional[str]:
    """Return content-type decor value."""
    header_decor = get_header_decor(t)
    if not header_decor:
        return None

    if 'content-type' in header_decor:
        return header_decor['content-type']

    return None


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


def get_backend_decor(t: typing.Any) -> Backends:
    """Return backend decor value."""
    return typing.cast(Backends, get_decor(t, 'backend'))
