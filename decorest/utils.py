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
"""Utility functions."""
import collections
import copy
import inspect
import logging as LOG
import re
import typing

from decorest.types import ArgsDict, StrDict


class CaseInsensitiveDict(typing.MutableMapping[str, typing.Any]):
    """
    Case insensitive dict for storing header values.

    Mostly modeled after CaseInsensitiveDict in:
        https://github.com/kennethreitz/requests
    """
    __original: typing.MutableMapping[str, typing.Any]

    def __init__(self, data: StrDict = {}, **kwargs: typing.Any) -> None:
        """Construct dict."""
        self.__original = dict()
        self.update(data, **kwargs)

    def __setitem__(self, key: str, value: typing.Any) -> None:
        """Set item under key."""
        self.__original[key.lower()] = (key, value)

    def __getitem__(self, key: str) -> typing.Any:
        """Get item for key."""
        return self.__original[key.lower()][1]

    def __delitem__(self, key: str) -> None:
        """Delete item with key."""
        del self.__original[key.lower()]

    def __contains__(self, key: str) -> bool:  # type: ignore[override]
        """Check if key exists."""
        return key.lower() in self.__original

    def __iter__(self) -> typing.Iterator[str]:
        """Return key iterator."""
        return (stored_key for stored_key, _ in self.__original.values())

    def __len__(self) -> int:
        """Return number of keys."""
        return len(self.__original)

    def __eq__(self, d: StrDict) -> bool:  # type: ignore[override]
        """Compare with another dict."""
        if isinstance(d, collections.abc.Mapping):
            d = CaseInsensitiveDict(d)
        else:
            raise NotImplementedError

        return dict(self.iteritems_lower()) == dict(d.iteritems_lower())

    def __repr__(self) -> str:
        """Return dict representation."""
        return f'<{self.__class__.__name__} {dict(self.items())}>'

    def iteritems_lower(self) \
            -> typing.Iterable[typing.Tuple[str, typing.Any]]:
        """Iterate over lower case keys."""
        return ((lkey, keyval[1])
                for (lkey, keyval) in self.__original.items())


def render_path(path: str, args: ArgsDict) -> str:
    """Render REST path from *args."""
    LOG.debug('RENDERING PATH FROM: %s,  %s', path, args)
    result = path
    matches = re.search(r'{([^}.]*)}', result)
    while matches:
        path_token = matches.group(1)
        if path_token not in args:
            raise ValueError("Missing argument %s in REST call." % path_token)
        result = re.sub('{%s}' % path_token, str(args[path_token]), result)
        matches = re.search(r'{([^}.]*)}', result)
    return result


def dict_from_args(func: typing.Callable[..., typing.Any],
                   *args: typing.Any) -> ArgsDict:
    """Convert function arguments to a dictionary."""
    result = {}

    parameters = inspect.signature(func).parameters
    idx = 0
    for name, parameter in parameters.items():
        if idx < len(args):
            # Add bound arguments to the dictionary
            result[name] = args[idx]
            idx += 1
        elif parameter.default is not inspect.Parameter.empty:
            # Add any default arguments if were left unbound in method call
            result[name] = parameter.default
            idx += 1
        else:
            pass

    return result


def merge_dicts(*dict_args: typing.Any) \
        -> typing.MutableMapping[typing.Any, typing.Any]:
    """
    Merge all dicts passed as arguments, skips None objects.

    Repeating keys will replace the keys from previous dicts.
    """
    result = None
    for dictionary in dict_args:
        if dictionary is not None:
            if result is None:
                result = copy.deepcopy(dictionary)
            else:
                result.update(dictionary)
    if result is None:
        result = {}
    return result


def merge_header_dicts(*dict_args: typing.Any) \
        -> typing.Dict[typing.Any, typing.Any]:
    """
    Merge all dicts passed as arguments, skips None objects.

    Repeating key values will be appended to the existing keys.
    """
    result = None
    for dictionary in dict_args:
        if dictionary is not None:
            if result is None:
                result = copy.deepcopy(dictionary)
            else:
                for k, v in dictionary.items():
                    if k in result:
                        if isinstance(result[k], list):
                            if isinstance(v, list):
                                result[k].extend(v)
                            else:
                                result[k].append(v)
                        else:
                            result[k] = [result[k], v]
                    else:
                        result[k] = v

    if result is None:
        result = {}

    return result


def normalize_url(url: str) -> str:
    """Make sure the url is in correct form."""
    result = url

    if not result.endswith("/"):
        result = result + "/"

    return result
