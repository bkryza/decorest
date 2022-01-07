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


class APIOne(RestClient):
    """API One client"""
    @GET('stuff/{what}')
    @on(200, lambda r: r.json())
    def get(self, what: str) -> typing.Any:
        """Get what"""


class APITwo(RestClient):
    """API One client"""
    @PUT('stuff/{what}')
    @body('body')
    def put(self, sth: str, body: bytes) -> typing.Any:
        """Put sth"""


class APIThree(RestClient):
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
class InheritedClient(APITwo, APIOne, APIThree):
    ...


def test_api_inheritance_properties() -> None:
    """
    Check that API inheritance works.
    """

    client = InheritedClient()

    assert client.backend_ == 'httpx'
    assert client.endpoint_ == 'https://example.com'

    client = InheritedClient(backend='requests',
                             endpoint="https://patches.example.com")

    assert client.backend_ == 'requests'
    assert client.endpoint_ == 'https://patches.example.com'


def test_api_inheritance_basic(respx_mock) -> None:
    """

    """
    client = InheritedClient()

    expected = dict(id=1, name='thing1')
    req = respx_mock.get("https://example.com/stuff/thing1")\
                    .mock(return_value=httpx.Response(200, content=json.dumps(expected)))

    res = client.get('thing1')

    assert req.called is True
    assert res == expected


def test_api_inheritance_custom_endpoint(respx_mock) -> None:
    """

    """
    client = InheritedClient(endpoint='https://patches.example.com')

    req = respx_mock.patch("https://patches.example.com/stuff/thing1")\
                    .mock(return_value=httpx.Response(204))

    res = client.patch('thing1',
                       body=json.loads('{"id": 1, "name": "thing2"}'))

    assert req.called is True
    assert res is True

    req = respx_mock.patch("https://patches.example.com/stuff/thing1")\
                    .mock(return_value=httpx.Response(500))

    res = client.patch('thing1',
                       body=json.loads('{"id": 1, "notname": "thing2"}'))

    assert req.called is True
    assert not res
