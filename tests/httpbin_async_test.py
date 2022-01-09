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
import asyncio
import pprint
from operator import methodcaller

import pytest
import time
import os
import sys
import json

import httpx
from httpx import BasicAuth

from requests.structures import CaseInsensitiveDict

from decorest import __version__, HttpStatus, HTTPErrorWrapper
from requests import cookies
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../examples")
from httpbin.httpbin_async_client import HttpBinAsyncClient, parse_image


@pytest.fixture
def client() -> HttpBinAsyncClient:
    # Give Docker and HTTPBin some time to spin up
    time.sleep(2)

    host = os.environ["HTTPBIN_HOST"]
    port = os.environ["HTTPBIN_80_TCP_PORT"]

    return HttpBinAsyncClient("http://{host}:{port}".format(host=host,
                                                            port=port))


@pytest.fixture
def basic_auth_client():
    # Give Docker and HTTPBin some time to spin up
    host = os.environ["HTTPBIN_HOST"]
    port = os.environ["HTTPBIN_80_TCP_PORT"]

    client = HttpBinAsyncClient("http://{host}:{port}".format(host=host,
                                                              port=port),
                                auth=BasicAuth('user', 'password'))

    return client


@pytest.mark.asyncio
async def test_ip(client):
    """
    """
    res = await client.ip()

    assert "origin" in res


@pytest.mark.asyncio
async def test_ip_head(client):
    """
    """
    res = await client.head_ip()

    assert res


@pytest.mark.asyncio
async def test_ip_options(client):
    """
    """
    res = await client.options_ip()

    assert sorted(res['allow'].split(", ")) == ['GET', 'HEAD', 'OPTIONS']


@pytest.mark.asyncio
async def test_ip_repeat(client):
    """
    """
    res = await client.ip_repeat()

    for ip in res:
        assert "origin" in ip


@pytest.mark.asyncio
async def test_uuid(client):
    """
    """
    res = await client.uuid()

    assert "uuid" in res


@pytest.mark.asyncio
async def test_user_agent(client):
    """
    """
    res = await client.user_agent()

    assert res['user-agent'] == 'decorest/{v}'.format(v=__version__)


@pytest.mark.asyncio
async def test_headers(client):
    """
    """
    def ci(d):
        return CaseInsensitiveDict(d)

    # Check
    res = await client.headers(header={'A': 'AA', 'B': 'CC'})

    assert ci(
        res['headers'])['User-Agent'] == 'decorest/{v}'.format(v=__version__)
    assert ci(res['headers'])['A'] == 'AA'
    assert ci(res['headers'])['B'] == 'CC'

    # Check with other values
    res = await client.headers(header={'A': 'DD', 'B': 'EE'})

    assert ci(res['headers'])['A'] == 'DD'
    assert ci(res['headers'])['B'] == 'EE'

    # Check method default header value
    res = await client.headers()

    assert ci(res['headers'])['B'] == 'BB'

    # Check passing header value in arguments
    res = await client.headers_in_args('1234', 'ABCD')

    assert ci(res['headers'])['First'] == '1234'
    assert ci(res['headers'])['SecondHeader'] == 'ABCD'


@pytest.mark.asyncio
async def test_get(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = await client.get(query=data)

    assert res["args"] == data


@pytest.mark.asyncio
async def test_post(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = await client.post(data, content='application/json', query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.asyncio
async def test_post_form(client):
    """
    """
    res = await client.post_form("value1", "value2", "value3")

    assert res["form"]["key1"] == "value1"
    assert res["form"]["key2"] == "value2"
    assert res["form"]["key3"] == "value3"


@pytest.mark.asyncio
async def test_post_multipart(client):
    """
    """
    file = 'tests/testdata/multipart.dat'

    with open(file, 'rb') as f:
        res = await client.post(None,
                                files={'test': ('filename', f, 'text/plain')})

    with open(file, 'rb') as f:
        assert res["files"]["test"] == f.read().decode("utf-8")


@pytest.mark.asyncio
async def test_post_multipart_decorators(client):
    """
    """
    file = 'tests/testdata/multipart.dat'

    with open(file, 'rb') as f:
        res = await client.post_multipart(bytes('TEST1', 'utf-8'),
                                          bytes('TEST2', 'utf-8'),
                                          ('filename', f, 'text/plain'))

    assert res["files"]["part1"] == 'TEST1'
    assert res["files"]["part2"] == 'TEST2'
    with open(file, 'rb') as f:
        assert res["files"]["test"] == f.read().decode("utf-8")


@pytest.mark.asyncio
async def test_patch(client):
    """
    """
    data = "ABCD"
    res = await client.patch(data, content="text/plain")

    assert res["data"] == data


@pytest.mark.asyncio
async def test_put(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = await client.put(data, content="application/json", query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.asyncio
async def test_multi_put(client):
    """
    """
    request_count = 100
    async with client._async_session() as s:
        reqs = [
            asyncio.ensure_future(
                s.put({i: str(i)}, content="application/json"))
            for i in range(0, request_count)
        ]

        reqs_result = await asyncio.gather(*reqs)

        keys = []
        for res in reqs_result:
            keys.append(int(list(res["json"].keys())[0]))

        assert keys == list(range(0, request_count))


@pytest.mark.asyncio
async def test_delete(client):
    """
    """
    data = {"a": "b", "c": "1"}
    await client.delete(query=data)


@pytest.mark.asyncio
async def test_anything(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = await client.anything(data, content="application/json", query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.asyncio
async def test_anything_anything(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = await client.anything_anything("something",
                                         data,
                                         content="application/json",
                                         query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.asyncio
async def test_encoding_utf(client):
    """
    """
    # TODO - add charset decorator


@pytest.mark.asyncio
async def test_gzip(client):
    """
    """
    res = await client.gzip()

    assert json.loads(res)['gzipped'] is True


@pytest.mark.asyncio
async def test_deflate(client):
    """
    """
    res = await client.deflate()

    assert json.loads(res)['deflated'] is True


@pytest.mark.asyncio
async def test_brotli(client):
    """
    """
    res = await client.brotli()

    assert json.loads(res)['brotli'] is True


@pytest.mark.asyncio
async def test_status(client):
    """
    """
    assert 418 == await client.status_code(418)


@pytest.mark.asyncio
async def test_response_headers(client):
    """
    """
    res = await client.response_headers('HTTP', 'BIN')

    assert res['firstName'] == 'HTTP'
    assert res['lastName'] == 'BIN'
    assert res['nickname'] == 'httpbin'


@pytest.mark.asyncio
async def test_redirect(client):
    """
    """
    res = await client.redirect(2,
                                on={302: lambda r: 'REDIRECTED'},
                                follow_redirects=False)

    assert res == 'REDIRECTED'


@pytest.mark.asyncio
async def test_redirect_to(client):
    """
    """
    res = await client.redirect_to('http://httpbin.org',
                                   on={302: lambda r: 'REDIRECTED'},
                                   follow_redirects=False)

    assert res == 'REDIRECTED'


@pytest.mark.asyncio
async def test_redirect_to_foo(client):
    """
    """
    res = await client.redirect_to_foo('http://httpbin.org',
                                       307,
                                       on={307: lambda r: 'REDIRECTED'},
                                       follow_redirects=False)

    assert res == 'REDIRECTED'


@pytest.mark.asyncio
async def test_relative_redirect(client):
    """
    """
    res = await client.relative_redirect(
        1, on={302: lambda r: r.headers['Location']}, follow_redirects=False)

    assert res == '/get'


@pytest.mark.asyncio
async def test_absolute_redirect(client):
    """
    """
    res = await client.absolute_redirect(
        1, on={302: lambda r: r.headers['Location']}, follow_redirects=False)

    assert res.endswith('/get')


@pytest.mark.asyncio
async def test_max_redirect(client):
    """
    """
    async with client.async_session_(max_redirects=1) as s:
        with pytest.raises(HTTPErrorWrapper) as e:
            await s.redirect(5, on={302: lambda r: 'REDIRECTED'})

        assert isinstance(e.value.wrapped, httpx.TooManyRedirects)


@pytest.mark.asyncio
async def test_cookies(client):
    """
    """
    jar = cookies.RequestsCookieJar()
    jar.set('cookie1', 'A', path='/cookies')
    jar.set('cookie2', 'B', path='/fruits')
    res = await client.cookies(cookies=jar)

    assert res['cookies']['cookie1'] == 'A'
    assert 'cookie2' not in res['cookies']


@pytest.mark.asyncio
async def test_cookies_set(client):
    """
    """
    res = await client.cookies_set(query={"cookie1": "A", "cookie2": "B"})

    assert res["cookies"]["cookie1"] == "A"
    assert res["cookies"]["cookie2"] == "B"


@pytest.mark.asyncio
async def test_cookies_session(client):
    """
    """
    s = client._async_session()
    pprint.pprint(type(s))
    res = await s.cookies_set(query={"cookie1": "A", "cookie2": "B"})

    assert res["cookies"]["cookie1"] == "A"
    assert res["cookies"]["cookie2"] == "B"

    res = await s.cookies()

    assert res["cookies"]["cookie1"] == "A"
    assert res["cookies"]["cookie2"] == "B"

    await s._close()


@pytest.mark.asyncio
async def test_cookies_session_with_contextmanager(client):
    """
    """
    async with client.async_session_() as s:
        s._backend_session.verify = False
        res = await s.cookies_set(query={"cookie1": "A", "cookie2": "B"})

        assert res["cookies"]["cookie1"] == "A"
        assert res["cookies"]["cookie2"] == "B"

        res = await s.cookies(follow_redirects=False)

        assert res["cookies"]["cookie1"] == "A"
        assert res["cookies"]["cookie2"] == "B"


@pytest.mark.asyncio
async def test_cookies_delete(client):
    """
    """
    await client.cookies_set(query={"cookie1": "A", "cookie2": "B"})
    await client.cookies_delete(query={"cookie1": None})
    res = await client.cookies()

    assert "cookie1" not in res["cookies"]


@pytest.mark.asyncio
async def test_basic_auth(client, basic_auth_client):
    """
    """
    with pytest.raises(HTTPErrorWrapper) as e:
        res = await client.basic_auth('user', 'password')

    assert isinstance(e.value, HTTPErrorWrapper)

    res = await basic_auth_client.basic_auth('user', 'password')
    assert res['authenticated'] is True


@pytest.mark.asyncio
async def test_basic_auth_with_session(client, basic_auth_client):
    """
    """
    with basic_auth_client._session() as s:
        res = await s.basic_auth('user', 'password')

    assert res['authenticated'] is True


@pytest.mark.asyncio
async def test_hidden_basic_auth(client):
    """
    """
    res = await client.hidden_basic_auth('user',
                                         'password',
                                         auth=BasicAuth('user', 'password'))

    assert res['authenticated'] is True


@pytest.mark.asyncio
async def test_digest_auth_algorithm(client):
    """
    """
    auth = httpx.DigestAuth('user', 'password')

    res = await client.digest_auth_algorithm('auth',
                                             'user',
                                             'password',
                                             'MD5',
                                             auth=auth)

    assert res['authenticated'] is True


@pytest.mark.asyncio
async def test_digest_auth(client):
    """
    """
    auth = httpx.DigestAuth('user', 'password')

    res = await client.digest_auth('auth', 'user', 'password', auth=auth)

    assert res['authenticated'] is True


@pytest.mark.asyncio
async def test_stream_n(client):
    """
    """
    count = 0
    async with client.async_session_() as s:
        r = await s.stream_n(5)
        async for _ in r.aiter_lines():
            count += 1

    assert count == 5


@pytest.mark.asyncio
async def test_delay(client):
    """
    """
    with pytest.raises(HTTPErrorWrapper):
        await client.delay(5)

    try:
        await client.delay(1)
        await client.delay(3, timeout=4)
    except HTTPErrorWrapper:
        pytest.fail("Operation should not have timed out")


@pytest.mark.asyncio
async def test_drip(client):
    """
    """
    content = []
    async with client.async_session_() as s:
        r = await s.drip(10, 5, 1, 200)
        async for b in r.aiter_raw():
            content.append(b)

    assert len(content) == 10


@pytest.mark.asyncio
async def test_range(client):
    """
    """
    content = []

    async with client.async_session_() as s:
        r = await s.range(128, 1, 2, header={"Range": "bytes=10-19"})
        async for b in r.aiter_raw():
            content.append(b)

    assert len(content) == 5


@pytest.mark.asyncio
async def test_html(client):
    """
    """
    res = await client.html(
        on={200: lambda r: (r.headers['content-type'], r.content)})

    assert res[0] == 'text/html; charset=utf-8'
    assert res[1].decode("utf-8").count(
        '<h1>Herman Melville - Moby-Dick</h1>') == 1


@pytest.mark.asyncio
async def test_robots_txt(client):
    """
    """
    res = await client.robots_txt()

    assert "Disallow: /deny" in res


@pytest.mark.asyncio
async def test_deny(client):
    """
    """
    res = await client.deny()

    assert "YOU SHOULDN'T BE HERE" in res


@pytest.mark.asyncio
async def test_cache(client):
    """
    """
    status_code = await client.cache(
        header={'If-Modified-Since': 'Sat, 16 Aug 2015 08:00:00 GMT'},
        on={HttpStatus.ANY: lambda r: r.status_code})

    assert status_code == 304


@pytest.mark.asyncio
async def test_cache_n(client):
    """
    """
    res = await client.cache_n(10)

    assert 'Cache-Control' not in res['headers']


@pytest.mark.asyncio
async def test_etag(client):
    """
    """
    status_code = await client.etag(
        'etag',
        header={'If-Match': 'notetag'},
        on={HttpStatus.ANY: lambda r: r.status_code})

    assert status_code == 412

    status_code = await client.etag(
        'etag',
        header={'If-Match': 'etag'},
        on={HttpStatus.ANY: lambda r: r.status_code})

    assert status_code == 200


@pytest.mark.asyncio
async def test_bytes(client):
    """
    """
    content = await client.stream_bytes(128)

    assert len(content) == 128


@pytest.mark.asyncio
async def test_stream_bytes(client):
    """
    """
    content = await client.stream_bytes(128)

    assert len(content) == 128


@pytest.mark.asyncio
async def test_links(client):
    """
    """
    html = await client.links(10, follow_redirects=True)

    assert html.count('href') == 10 - 1


@pytest.mark.asyncio
async def test_image(client):
    """
    """
    img = await client.image(accept='image/jpeg', on={200: parse_image})

    assert img.format == 'JPEG'

    img = await client.image_png()

    assert img.format == 'PNG'

    img = await client.image_jpeg()

    assert img.format == 'JPEG'

    img = await client.image_webp()

    assert img.format == 'WEBP'


@pytest.mark.asyncio
async def test_xml(client):
    """
    """
    slideshow = await client.xml(on={200: lambda r: ET.fromstring(r.text)})

    assert slideshow.tag == 'slideshow'
