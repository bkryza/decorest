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

from .GET import GET
from .POST import POST
from .PUT import PUT
from .PATCH import PATCH
from .DELETE import DELETE
from .UPDATE import UPDATE
from .HEAD import HEAD
from .OPTIONS import OPTIONS
from .client import RestClient, HttpMethod, HttpStatus
from .decorators import query, body, header, auth, on, accept, content
from .decorators import endpoint, timeout

__version__ = (0, 0, 2)

decorest_version = '.'.join(map(str,__version__))


