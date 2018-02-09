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

from decorest import RestClient
from decorest import GET
from decorest import header, query, accept, endpoint, content

import pytest


class DogClient(RestClient):
    def __init__(self, endpoint):
        super(DogClient, self).__init__(endpoint)

    @GET('breed/{breed_name}/list')
    def list_subbreeds(self, breed_name):
        """List all sub-breeds"""

    def plain_list_subbreeds(self, breed_name):
        """List all sub-breeds"""

    @GET('breed')
    @query('a')
    @query('b')
    @query('c', 'd')
    def queries(self, a, b, c=2):
        """So many queries"""

    def plain_queries(self, a, b, c=2):
        """So many queries"""

    @GET('breed')
    @content('application/json')
    @header('A', 'B')
    @accept('application/xml')
    def headers(self, a, b, c):
        """Headers"""

    def plain_headers(self, a, b, c):
        """Headers"""


def test_introspection():
    """
    Make sure the decorators maintain the original methods
    signatures.
    """

    assert(DogClient.list_subbreeds.__doc__ ==
           DogClient.plain_list_subbreeds.__doc__)

    d = DogClient.list_subbreeds.__dict__
    if '__wrapped__' in d:
        del d['__wrapped__']
    assert(d == DogClient.plain_list_subbreeds.__dict__)

    assert(DogClient.queries.__doc__ == DogClient.plain_queries.__doc__)

    d = DogClient.queries.__dict__
    if '__wrapped__' in d:
        del d['__wrapped__']
    if '__decorest__' in d:
        del d['__decorest__']
    assert(d == DogClient.plain_queries.__dict__)


    assert(DogClient.headers.__doc__ == DogClient.plain_headers.__doc__)

    d = DogClient.headers.__dict__
    if '__wrapped__' in d:
        del d['__wrapped__']
    if '__decorest__' in d:
        del d['__decorest__']
    assert(d == DogClient.plain_headers.__dict__)



