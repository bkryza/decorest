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
"""GET Http method decorator."""

from functools import wraps

from .decorators import HttpMethodDecorator, set_decor
from .types import HttpMethod


class GET(HttpMethodDecorator):
    """GET HTTP method decorator."""
    def __init__(self, path):
        """Initialize with endpoint relative path."""
        super(GET, self).__init__(path)

    def __call__(self, func):
        """Callable operator."""
        set_decor(func, 'http_method', HttpMethod.GET)

        @wraps(func)
        def get_decorator(*args, **kwargs):
            return super(GET, self).call(func, *args, **kwargs)

        return get_decorator
