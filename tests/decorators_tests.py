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
import typing

import pytest
import functools

from decorest import RestClient, HttpMethod
from decorest import GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
from decorest import accept, content, endpoint, form, header, query, stream
from decorest.decorators import get_decor, get_header_decor, get_endpoint_decor, get_form_decor, get_query_decor, \
    get_stream_decor, get_on_decor, get_method_decor


@accept('application/json')
@content('application/xml')
@header('X-Auth-Key', 'ABCD')
@endpoint('https://dog.ceo/')
class DogClient(RestClient):
    """DogClient client"""

    @GET('breed/{breed_name}/list')
    def list_subbreeds(self, breed_name: str) -> typing.Any:
        """List all sub-breeds"""

    def plain_list_subbreeds(self, breed_name: str) -> typing.Any:
        """List all sub-breeds"""

    @GET('breed')
    @query('a')
    @query('b')
    @query('c', 'd')
    def queries(self, a: str, b: str, c: int = 2) -> typing.Any:
        """So many queries"""

    def plain_queries(self, a: str, b: str, c: int = 2) -> typing.Any:
        """So many queries"""

    @GET('breed')
    @content('application/json')
    @header('A', 'B')
    @accept('application/xml')
    def headers(self, a: str, b: str, c: str) -> typing.Any:
        """Headers"""

    def plain_headers(self, a: str, b: str, c: str) -> None:
        """Headers"""

    @GET('get')
    def get(self, a: str) -> typing.Any:
        """Get something"""

    @POST('post')
    def post(self, a: str) -> None:
        """Post something"""

    @POST('post')
    @form('key1')
    @form('key2', 'keyTwo')
    def post_form(self, key1: str, key2: str) -> None:
        """Post 2 keys"""

    @PUT('put')
    def put(self, a: str) -> None:
        """Put something"""

    @PATCH('patch')
    def patch(self, a: str) -> None:
        """Patch something"""

    @DELETE('delete')
    def delete(self, a: str) -> None:
        """Delete something"""

    @HEAD('head')
    def head(self, a: str) -> typing.Any:
        """Heads up"""

    @OPTIONS('options')
    def options(self, a: str) -> typing.Any:
        """What can I do?"""

    @GET('stream/{n}/{m}')
    @stream
    @query('size')
    @query('offset', 'off')
    def stream_range(self, n: int, m: int,
                     size: int, offset: int) -> typing.Any:
        """Get data range"""

    def plain_stream_range(self, n: int, m: int,
                           size: int, offset: int) -> typing.Any:
        """Get data range"""


def test_set_decor() -> None:
    """
    Check that decorators store proper values in the decorated
    class and methods.
    """

    assert get_on_decor(DogClient) is None

    headers = get_header_decor(DogClient)
    assert headers is not None
    assert headers['Accept'] == 'application/json'
    assert headers['accept'] == 'application/json'
    assert headers['content-Type'] == 'application/xml'
    assert headers['x-auth-key'] == 'ABCD'

    assert get_endpoint_decor(DogClient) == 'https://dog.ceo/'

    assert get_method_decor(DogClient.get) == HttpMethod.GET
    assert get_method_decor(DogClient.post) == HttpMethod.POST
    assert get_method_decor(DogClient.put) == HttpMethod.PUT
    assert get_method_decor(DogClient.patch) == HttpMethod.PATCH
    assert get_method_decor(DogClient.delete) == HttpMethod.DELETE
    assert get_method_decor(DogClient.head) == HttpMethod.HEAD
    assert get_method_decor(DogClient.options) == HttpMethod.OPTIONS
    assert get_method_decor(DogClient.stream_range) == HttpMethod.GET

    assert get_form_decor(DogClient.post_form) == {
        'key1': 'key1',
        'key2': 'keyTwo'
    }
    assert get_query_decor(DogClient.queries) == {
        'a': 'a',
        'b': 'b',
        'c': 'd'
    }

    assert get_stream_decor(DogClient.stream_range) is True
    assert get_query_decor(DogClient.stream_range) == {
        'offset': 'off',
        'size': 'size'
    }


def test_endpoint_decorator() -> None:
    """
    Tests if endpoint decorator sets the service endpoint properly.
    """

    default_client = DogClient()

    assert default_client.endpoint == 'https://dog.ceo/'

    custom_client = DogClient('http://dogceo.example.com')

    assert custom_client.endpoint == 'http://dogceo.example.com'


def test_introspection() -> None:
    """
    Make sure the decorators maintain the original method
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
