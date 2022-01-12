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
"""Various types related to HTTP and REST."""

import enum
import typing

import typing_extensions

DEnum = enum.Enum
DIntEnum = enum.IntEnum


class HttpMethod(DEnum):
    """Enum with HTTP methods."""

    GET = 'GET',
    POST = 'POST',
    PUT = 'PUT',
    PATCH = 'PATCH',
    DELETE = 'DELETE',
    HEAD = 'HEAD',
    OPTIONS = 'OPTIONS',
    INVALID = ''  # without this 'OPTIONS' becomes 'O'

    def __str__(self) -> str:
        """Return string representation."""
        return typing.cast(str, self.value[0])


class HttpStatus(DIntEnum):
    """Enum with HTTP error code classes."""

    INFORMATIONAL_RESPONSE = 1,
    SUCCESS = 2,
    REDIRECTION = 3,
    CLIENT_ERROR = 4,
    SERVER_ERROR = 5,
    ANY = 999  # Same as Ellipsis '...'


if typing.TYPE_CHECKING:
    # If not available, these imports will be ignored through settings
    # in mypy.ini
    import requests
    import httpx

ArgsDict = typing.MutableMapping[str, typing.Any]
StrDict = typing.Mapping[str, typing.Any]
Backends = typing_extensions.Literal['requests', 'httpx']
AuthTypes = typing.Union['requests.auth.AuthBase', 'httpx.AuthTypes']
HeaderDict = typing.Mapping[str, typing.Union[str, typing.List[str]]]
SessionTypes = typing.Union['requests.Session', 'httpx.Client']
HTTPErrors = typing.Union['requests.HTTPError', 'httpx.HTTPStatusError']

TDecor = typing.TypeVar('TDecor', bound=typing.Callable[..., typing.Any])

if typing.TYPE_CHECKING:

    class ellipsis(enum.Enum):  # noqa N801
        """
        Ellipsis type for typechecking.

        A workaround to enable specifying ellipsis as possible type
        for the 'on' decorator.
        """
        Ellipsis = "..."

    Ellipsis = ellipsis.Ellipsis
else:
    ellipsis = type(Ellipsis)
