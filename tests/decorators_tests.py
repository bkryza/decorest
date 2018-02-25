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

from requests.auth import HTTPBasicAuth
import pytest
import functools

from decorest import RestClient, HttpMethod
from decorest import GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
from decorest import header, query, accept, endpoint, content, auth, stream
from decorest.decorators import get_decor


@accept('application/json')
@content('application/xml')
@header('X-Auth-Key', 'ABCD')
@endpoint('https://dog.ceo/')
@auth(HTTPBasicAuth('user', 'password'))
class DogClient(RestClient):
    """DogClient client"""

    def __init__(self, endpoint=None):
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

    @GET('get')
    def get(self, a):
        """Get something"""

    @POST('post')
    def post(self, a):
        """Post something"""

    @PUT('put')
    def put(self, a):
        """Put something"""

    @PATCH('patch')
    def patch(self, a):
        """Patch something"""

    @DELETE('delete')
    def delete(self, a):
        """Delete something"""

    @HEAD('head')
    def head(self, a):
        """Heads up"""

    @OPTIONS('options')
    def options(self, a):
        """What can I do?"""

    @GET('stream/{n}/{m}')
    @stream
    @query('size')
    @query('offset', 'off')
    def stream_range(self, n, m, size, offset):
        """Get data range"""

    def plain_stream_range(self, n, m, size, offset):
        """Get data range"""


def test_set_decor():
    """
    Check that decorators store proper values in the decorated
    class and methods.
    """

    assert get_decor(DogClient, 'header')['Accept'] == 'application/json'
    assert get_decor(DogClient, 'header')['content-Type'] == 'application/xml'
    assert get_decor(DogClient, 'header')['x-auth-key'] == 'ABCD'
    assert get_decor(DogClient, 'endpoint') == 'https://dog.ceo/'
    assert get_decor(DogClient, 'auth') == HTTPBasicAuth('user', 'password')

    assert get_decor(DogClient.get, 'http_method') == HttpMethod.GET
    assert get_decor(DogClient.post, 'http_method') == HttpMethod.POST
    assert get_decor(DogClient.put, 'http_method') == HttpMethod.PUT
    assert get_decor(DogClient.patch, 'http_method') == HttpMethod.PATCH
    assert get_decor(DogClient.delete, 'http_method') == HttpMethod.DELETE
    assert get_decor(DogClient.head, 'http_method') == HttpMethod.HEAD
    assert get_decor(DogClient.options, 'http_method') == HttpMethod.OPTIONS
    assert get_decor(DogClient.stream_range, 'http_method') == HttpMethod.GET

    assert get_decor(DogClient.stream_range, 'stream') is True
    assert get_decor(DogClient.stream_range, 'query') == {
        'offset': 'off', 'size': 'size'}


def test_endpoint_decorator():
    """
    Tests if endpoint decorator sets the service endpoint properly.
    """

    default_client = DogClient()

    assert default_client.endpoint == 'https://dog.ceo/'

    custom_client = DogClient('http://dogceo.example.com')

    assert custom_client.endpoint == 'http://dogceo.example.com'


def test_introspection():
    """
    Make sure the decorators maintain the original methods
    signatures.
    """
    client = DogClient()

    assert DogClient.__name__ == 'DogClient'
    assert client.__class__.__name__ == 'DogClient'
    assert DogClient.__doc__ == 'DogClient client'

    assert DogClient.list_subbreeds.__name__ == 'list_subbreeds'

    assert DogClient.list_subbreeds.__doc__ == DogClient.plain_list_subbreeds.__doc__
    assert DogClient.list_subbreeds.__module__ == DogClient.plain_list_subbreeds.__module__

    d = DogClient.list_subbreeds.__dict__
    if '__wrapped__' in d:
        del d['__wrapped__']
    if '__decorest__' in d:
        del d['__decorest__']
    assert d == DogClient.plain_list_subbreeds.__dict__

    assert DogClient.queries.__doc__ == DogClient.plain_queries.__doc__

    d = DogClient.queries.__dict__
    if '__wrapped__' in d:
        del d['__wrapped__']
    if '__decorest__' in d:
        del d['__decorest__']
    assert d == DogClient.plain_queries.__dict__

    assert DogClient.headers.__doc__ == DogClient.plain_headers.__doc__

    d = DogClient.headers.__dict__
    if '__wrapped__' in d:
        del d['__wrapped__']
    if '__decorest__' in d:
        del d['__decorest__']
    assert d == DogClient.plain_headers.__dict__

    assert DogClient.stream_range.__doc__ == DogClient.plain_stream_range.__doc__
    assert DogClient.stream_range.__module__ == DogClient.plain_stream_range.__module__

    d = DogClient.stream_range.__dict__
    if '__wrapped__' in d:
        del d['__wrapped__']
    if '__decorest__' in d:
        del d['__decorest__']
    assert d == DogClient.plain_stream_range.__dict__
