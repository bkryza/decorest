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
import typing

import pytest
import functools

from requests.auth import HTTPBasicAuth as r_HTTPBasicAuth
from httpx import BasicAuth as x_HTTPBasicAuth

from decorest import RestClient, HttpMethod, HTTPErrorWrapper, multipart, on, HttpRequest, CaseInsensitiveDict
from decorest import GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
from decorest import accept, backend, content, endpoint, form, header
from decorest import query, stream
from decorest.decorator_utils import get_backend_decor, get_header_decor, \
    get_endpoint_decor, get_form_decor, get_query_decor, \
    get_stream_decor, get_on_decor, get_method_decor, get_method_class_decor, get_multipart_decor, get_accept_decor, \
    get_content_decor, set_decor
from decorest.utils import merge_header_dicts


@accept('application/json')
@content('application/xml')
@header('X-Auth-Key', 'ABCD')
@endpoint('https://dog.ceo/')
@backend('requests')
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

    @POST('post')
    @multipart('part1')
    @multipart('part_2', 'part2')
    @multipart('test')
    async def post_multipart(self, part1, part_2, test):
        """Return multipart POST data."""

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
    def stream_range(self, n: int, m: int, size: int,
                     offset: int) -> typing.Any:
        """Get data range"""

    def plain_stream_range(self, n: int, m: int, size: int,
                           offset: int) -> typing.Any:
        """Get data range"""


def test_case_insensitive_dict() -> None:
    """
    Tests for case insensitive dict.
    """
    d = CaseInsensitiveDict()

    d['Accept'] = 'application/json'
    d['content-type'] = 'application/xml'
    assert d['accept'] == 'application/json'
    assert d['Content-Type'] == 'application/xml'
    assert 'accept' in d
    assert 'ACCEPT' in d
    assert 'CONTENT-TYPE' in d
    assert len(d) == 2

    d1 = CaseInsensitiveDict(accept='application/json', allow='*')
    assert d1['Accept'] == 'application/json'
    assert d1['Allow'] == '*'
    assert len(d1) == 2

    ds = {'Content-TYPE': 'application/json', 'aCCEPT': 'application/xml'}
    d2 = CaseInsensitiveDict(ds)
    assert d2['content-type'] == 'application/json'
    assert d2['Accept'] == 'application/xml'
    assert len(d2) == 2

    d3 = merge_header_dicts(d1, d2)
    assert d3['content-type'] == 'application/json'
    assert d3['accept'] == ['application/json', 'application/xml']
    assert d3['allow'] == '*'
    assert len(d3) == 3


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

    assert get_accept_decor(DogClient) == 'application/json'
    assert get_content_decor(DogClient) == 'application/xml'
    assert get_content_decor(DogClient.headers) == 'application/json'
    assert get_accept_decor(DogClient.headers) == 'application/xml'

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

    assert get_multipart_decor(DogClient.post_multipart) == {
        'part1': 'part1',
        'part_2': 'part2',
        'test': 'test'
    }

    assert get_query_decor(DogClient.queries) == {'a': 'a', 'b': 'b', 'c': 'd'}

    assert get_stream_decor(DogClient.stream_range) is True
    assert get_query_decor(DogClient.stream_range) == {
        'offset': 'off',
        'size': 'size'
    }

    assert get_backend_decor(DogClient) == 'requests'


def test_endpoint_decorator() -> None:
    """
    Tests if endpoint decorator sets the service endpoint properly.
    """

    default_client = DogClient()

    assert default_client.endpoint_ is None  # 'https://dog.ceo/'

    custom_client = DogClient('http://dogceo.example.com')

    assert custom_client.endpoint_ == 'http://dogceo.example.com'


def test_missing_endpoint_decorator() -> None:
    """
    """
    class EmptyClient(RestClient):
        """EmptyClient client"""
        @GET('{sth}')
        def get(self, sth: str) -> typing.Any:
            """Get sth"""

    with pytest.raises(ValueError) as e:
        default_client = EmptyClient()
        default_client.get('stuff')

    assert str(e.value) == 'Server endpoint was not provided.'


def test_invalid_on_decorator() -> None:
    """
    """
    with pytest.raises(TypeError) as e:

        class EmptyClient(RestClient):
            """EmptyClient client"""
            @GET('{sth}')
            @on('200', lambda x: x)
            def get(self, sth: str) -> typing.Any:
                """Get sth"""

        client = EmptyClient()

    assert str(e.value) == "Status in @on decorator must be integer or '...'."


def test_invalid_query_decorator() -> None:
    """
    """
    with pytest.raises(TypeError) as e:

        @query('{sthelse}')
        class EmptyClient(RestClient):
            """EmptyClient client"""
            @GET('{sth}')
            def get(self, sth: str) -> typing.Any:
                """Get sth"""

        client = EmptyClient()

    assert str(e.value) == "@query decorator can only be applied to methods."


def test_invalid_multipart_decorator() -> None:
    """
    """
    with pytest.raises(TypeError) as e:

        @multipart('{sthelse}')
        class EmptyClient(RestClient):
            """EmptyClient client"""
            @GET('{sth}')
            def get(self, sth: str) -> typing.Any:
                """Get sth"""

        client = EmptyClient()

    assert str(
        e.value) == "@multipart decorator can only be applied to methods."


def test_invalid_form_decorator() -> None:
    """
    """
    with pytest.raises(TypeError) as e:

        @form('{sthelse}')
        class EmptyClient(RestClient):
            """EmptyClient client"""
            @GET('{sth}')
            def get(self, sth: str) -> typing.Any:
                """Get sth"""

        client = EmptyClient()

    assert str(e.value) == "@form decorator can only be applied to methods."


def test_invalid_backend_decorator() -> None:
    """
    """
    with pytest.raises(TypeError) as e:

        class EmptyClient(RestClient):
            """EmptyClient client"""
            @GET('{sth}')
            @backend('http://example.com')
            def get(self, sth: str) -> typing.Any:
                """Get sth"""

        client = EmptyClient()

    assert str(e.value) == "@backend decorator can only be applied to classes."


def test_missing_path_argument() -> None:
    """
    """
    class EmptyClient(RestClient):
        """EmptyClient client"""
        @GET('{something}')
        def get(self, sth: str) -> typing.Any:
            """Get sth"""

    with pytest.raises(ValueError) as e:
        default_client = EmptyClient()
        default_client.get('stuff')

    assert str(e.value) == 'Missing argument something in REST call.'


def test_invalid_backend() -> None:
    """
    """
    with pytest.raises(ValueError) as e:
        client = DogClient(backend='yahl')

    assert str(e.value) == 'Invalid backend: yahl'


def test_invalid_client_named_args() -> None:
    """
    """
    with pytest.raises(ValueError) as e:
        client = DogClient(no_such_arg='foo')

    assert str(e.value) == "Invalid named arguments passed " \
                           "to the client: {'no_such_arg'}"


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


def test_get_method_class_decor() -> None:
    """

    """
    @endpoint('http://a.example.com')
    class A(RestClient):
        @GET('{a}')
        def a(self, a: str):
            ...

    class B(RestClient):
        @GET('{b}')
        def b(self, b: str):
            ...

    @endpoint('http://bb.example.com')
    class BB(B):
        @GET('{bb}')
        def bb(self, bb: str):
            ...

    class BBB(BB):
        @GET('{bbb}')
        def bbb(self, bbb: str):
            ...

    class BBB2(BB):
        @GET('{bbb2}')
        def bbb2(self, bbb2: str):
            ...

    class C(RestClient):
        @GET('{c}')
        def c(self, c: str):
            ...

    class CC(C):
        @GET('{cc}')
        def cc(self, cc: str):
            ...

    @endpoint('http://example.com')
    class Client(A, BBB, BBB2, CC):
        ...

    client = Client()

    assert get_method_class_decor(A.a, client,
                                  'endpoint') == 'http://a.example.com'
    assert get_method_class_decor(B.b, client,
                                  'endpoint') == 'http://bb.example.com'
    assert get_method_class_decor(BB.bb, client,
                                  'endpoint') == 'http://bb.example.com'
    assert get_method_class_decor(BBB.bbb, client,
                                  'endpoint') == 'http://example.com'
    assert get_method_class_decor(BBB2.bbb2, client,
                                  'endpoint') == 'http://example.com'
    assert get_method_class_decor(C.c, client,
                                  'endpoint') == 'http://example.com'
    assert get_method_class_decor(CC.cc, client,
                                  'endpoint') == 'http://example.com'


def test_authentication_settings() -> None:
    """
    Tests if authentication is properly configured.
    """
    r_client = DogClient(backend='requests')
    assert r_client['auth'] is None
    r_client['auth'] = r_HTTPBasicAuth('username', 'password')
    assert r_client['auth'] == r_HTTPBasicAuth('username', 'password')

    r_client_auth = DogClient(backend='requests',
                              auth=r_HTTPBasicAuth('username', 'password'))
    assert r_client_auth['auth'] == r_HTTPBasicAuth('username', 'password')

    r_session_auth = r_client_auth._session()
    assert r_session_auth['auth'] == r_HTTPBasicAuth('username', 'password')

    x_client = DogClient(backend='httpx')
    assert x_client['auth'] is None
    x_client['auth'] = x_HTTPBasicAuth('username', 'password')
    assert x_client['auth']._auth_header == \
           x_HTTPBasicAuth('username', 'password')._auth_header

    x_client_auth = DogClient(backend='httpx',
                              auth=x_HTTPBasicAuth('username', 'password'))
    assert x_client_auth['auth']._auth_header == \
           x_HTTPBasicAuth('username', 'password')._auth_header
    x_session_auth = x_client_auth._session()
    assert x_session_auth._auth._auth_header == \
           x_HTTPBasicAuth('username', 'password')._auth_header


def test_authentication_settings_deprecated() -> None:
    """
    Tests if authentication is properly configured.
    """

    r_client = DogClient(backend='requests')
    assert r_client.auth_() is None
    r_client._set_auth(r_HTTPBasicAuth('username', 'password'))
    assert r_client['auth'] == r_HTTPBasicAuth('username', 'password')

    assert r_client.auth_() == r_HTTPBasicAuth('username', 'password')

    assert r_client._auth() == r_HTTPBasicAuth('username', 'password')

    r_client_auth = DogClient(backend='requests',
                              auth=r_HTTPBasicAuth('username', 'password'))
    assert r_client_auth.auth_() == r_HTTPBasicAuth('username', 'password')

    assert r_client_auth._auth() == r_HTTPBasicAuth('username', 'password')

    r_session_auth = r_client_auth._session()
    assert r_session_auth._auth == r_HTTPBasicAuth('username', 'password')

    x_client = DogClient(backend='httpx')
    assert x_client._auth() is None
    x_client._set_auth(x_HTTPBasicAuth('username', 'password'))
    assert x_client._auth()._auth_header == \
           x_HTTPBasicAuth('username', 'password')._auth_header

    x_client_auth = DogClient(backend='httpx',
                              auth=x_HTTPBasicAuth('username', 'password'))
    assert x_client_auth._auth()._auth_header == \
           x_HTTPBasicAuth('username', 'password')._auth_header
    x_session_auth = x_client_auth._session()
    assert x_session_auth._auth._auth_header == \
           x_HTTPBasicAuth('username', 'password')._auth_header


def test_repr_methods():
    r_client = DogClient(backend='requests')
    assert repr(r_client) \
           == '<DogClient backend: requests endpoint: \'https://dog.ceo/\'>'

    x_client = DogClient(backend='httpx')
    assert repr(x_client) \
           == '<DogClient backend: httpx endpoint: \'https://dog.ceo/\'>'

    class MockClient(RestClient):
        def func(self, breed_name: str):
            return breed_name

    set_decor(MockClient.func, 'http_method', HttpMethod.GET)
    req = HttpRequest(MockClient.func,
                      'breed/{breed_name}/list',
                      args=(r_client, "dog"),
                      kwargs={})
    assert repr(req) == '<HttpRequest method: GET path: \'breed/dog/list\'>'

    with r_client.session_() as s:
        assert repr(s) == f'<RestClientSession client: {repr(r_client)}>'
