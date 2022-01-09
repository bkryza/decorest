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
"""Export module packages."""

from .DELETE import DELETE
from .GET import GET
from .HEAD import HEAD
from .OPTIONS import OPTIONS
from .PATCH import PATCH
from .POST import POST
from .PUT import PUT
from .client import RestClient
from .decorators import accept, backend, body, content, endpoint, form, header
from .decorators import multipart, on, query, stream, timeout
from .errors import HTTPErrorWrapper
from .request import HttpRequest
from .types import HttpMethod, HttpStatus
from .utils import CaseInsensitiveDict

__all__ = [
    'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'RestClient',
    'HTTPErrorWrapper', 'HttpMethod', 'HttpStatus', 'HttpRequest',
    'CaseInsensitiveDict', 'query', 'body', 'header', 'on', 'accept',
    'content', 'endpoint', 'timeout', 'stream', 'form', 'multipart', 'backend'
]

__version__ = "0.1.0"
