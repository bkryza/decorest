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
"""HEAD Http method decorator."""
import typing
from functools import wraps

from .decorators import HttpMethodDecorator, set_decor
from .types import HttpMethod, TDecor


class HEAD(HttpMethodDecorator):
    """HEAD HTTP method decorator."""
    def __init__(self, path: str):
        """Initialize with endpoint relative path."""
        super(HEAD, self).__init__(path)

    def __call__(self, func: TDecor) -> TDecor:
        """Callable operator."""
        set_decor(func, 'http_method', HttpMethod.HEAD)

        @wraps(func)
        def head_decorator(*args: typing.Any, **kwargs: typing.Any) \
                -> typing.Any:
            return super(HEAD, self).call(func, *args, **kwargs)

        return typing.cast(TDecor, head_decorator)
