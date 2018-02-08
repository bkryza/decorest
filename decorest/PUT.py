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


class PUT(HttpMethodDecorator):

    def __init__(self, path):
        super(PUT, self).__init__(path)

    def __call__(self, func):
        def put_decorator(*args, **kwargs):
            func._http__method = HttpMethod.PUT
            return super(PUT, self).call(func, *args, **kwargs)
        return put_decorator
