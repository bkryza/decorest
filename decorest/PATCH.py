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

from .client import HttpMethod
from .decorators import HttpMethodDecorator
from functools import wraps


class PATCH(HttpMethodDecorator):

    def __init__(self, path):
        super(PATCH, self).__init__(path)

    def __call__(self, func):
        @wraps(func)
        def patch_decorator(*args, **kwargs):
            func._http__method = HttpMethod.PATCH
            return super(PATCH, self).call(func, *args, **kwargs)
        return patch_decorator
