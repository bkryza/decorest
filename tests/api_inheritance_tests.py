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
import json
import pprint
import typing

import httpx
import pytest
import functools

from requests.auth import HTTPBasicAuth as r_HTTPBasicAuth
from httpx import BasicAuth as x_HTTPBasicAuth

from decorest import RestClient, on
from decorest import accept, backend, body, content, endpoint, header
from decorest import GET, PATCH, PUT


class A(RestClient):
    """API One client"""
    @GET('stuff/{sth}')
    @on(200, lambda r: r.json())
    def get(self, sth: str) -> typing.Any:
        """Get what"""


class B(RestClient):
    """API One client"""
    @PUT('stuff/{sth}')
    @body('body')
    @on(204, lambda _: True)
    def put_b(self, sth: str, body: bytes) -> typing.Any:
        """Put sth"""


@endpoint('https://put.example.com')
class BB(B):
    """API One client"""
    @PUT('stuff/{sth}')
    @body('body')
    @on(204, lambda _: True)
    def put_bb(self, sth: str, body: bytes) -> typing.Any:
        """Put sth"""


@endpoint('https://patches.example.com')
class C(RestClient):
    """API Three client"""
    @PATCH('stuff/{sth}')
    @body('body')
    @on(204, lambda _: True)
    @on(..., lambda _: False)
    def patch(self, sth: str, body: bytes) -> typing.Any:
        """Patch sth"""


@accept('application/json')
@content('application/xml')
@header('X-Auth-Key', 'ABCD')
@endpoint('https://example.com')
@backend('httpx')
class InheritedClient(A, BB, C):
    ...


def test_api_inheritance_properties() -> None:
    """
    Check that API inheritance works.
    """

    client = InheritedClient()

    assert client.backend_ == 'httpx'
    assert client.endpoint_ is None  # 'https://example.com'

    client = InheritedClient('https://patches.example.com', backend='requests')

    assert client.backend_ == 'requests'
    assert client.endpoint_ == 'https://patches.example.com'


@pytest.mark.parametrize("backend", ['httpx'])
def test_api_inheritance_basic(respx_mock, backend) -> None:
    """

    """
    client = InheritedClient(backend=backend)

    expected = dict(id=1, name='thing1')
    req = respx_mock.get("https://example.com/stuff/thing1")\
                    .mock(return_value=httpx.Response(200, content=json.dumps(expected)))

    res = client.get('thing1')

    assert req.called is True
    assert res == expected

    client = InheritedClient('https://example2.com', backend=backend)

    req = respx_mock.get('https://example2.com/stuff/thing1')\
                    .mock(return_value=httpx.Response(200, content=json.dumps(expected)))

    res = client.get('thing1')

    assert req.called is True
    assert res == expected


@pytest.mark.parametrize("backend", ['httpx'])
def test_api_inheritance_custom_endpoint(respx_mock, backend) -> None:
    """
    """
    client = InheritedClient(backend=backend)

    req = respx_mock.patch("https://patches.example.com/stuff/thing1")\
                    .mock(return_value=httpx.Response(204))

    res = client.patch('thing1',
                       body=json.loads('{"id": 1, "name": "thing2"}'))

    assert req.called is True
    assert res is True

    req = respx_mock.patch("https://patches.example.com/stuff/thing2")\
                    .mock(return_value=httpx.Response(500))

    res = client.patch('thing2',
                       body=json.loads('{"id": 1, "notname": "thing2"}'))

    assert req.called is True
    assert not res

    with client.session_() as s:
        res = s.patch('thing1', body=json.loads('{"id": 3, "name": "thing3"}'))
        assert req.called is True
        assert res is True

    req = respx_mock.patch("https://patches2.example.com/stuff/thing1")\
                    .mock(return_value=httpx.Response(204))
    with client.session_(endpoint="https://patches2.example.com") as s:
        res = s.patch('thing1', body=json.loads('{"id": 3, "name": "thing3"}'))
        assert req.called is True
        assert res is True

    redirect_headers = {
        'Location': 'https://patches3.example.com/stuff/thing1'
    }
    req = respx_mock.patch("https://patches.example.com/stuff/thing1").mock(
        return_value=httpx.Response(301, headers=redirect_headers))

    req_redirect \
        = respx_mock.patch("https://patches3.example.com/stuff/thing1").mock(
        return_value=httpx.Response(204))

    with client.session_() as s:
        res = s.patch('thing1', body=json.loads('{"id": 3, "name": "thing3"}'))
        assert req.called and req_redirect.called
        assert res is True

    req = respx_mock.put("https://put.example.com/stuff/thing1")\
                    .mock(return_value=httpx.Response(204))

    res = client.put_b('thing1',
                       body=json.loads('{"id": 1, "name": "thing2"}'))

    assert req.called is True
    assert res

    req = respx_mock.put("https://put.example.com/stuff/thing2")\
                    .mock(return_value=httpx.Response(204))

    res = client.put_bb('thing2',
                        body=json.loads('{"id": 1, "name": "thing2"}'))

    assert req.called is True
    assert res
