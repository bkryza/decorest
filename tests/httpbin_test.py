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

import pytest
import time
import os
import sys
import json
from decorest import decorest_version, HttpStatus
from requests import cookies
from requests.exceptions import ReadTimeout
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_toolbelt.multipart.encoder import MultipartEncoder
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../examples")
from httpbin.httpbin_client import HttpBinClient, parse_image

@pytest.fixture
def client():
    # Give Docker and HTTPBin some time to spin up
    time.sleep(5)
    httpbin_port = os.environ["KENNETHREITZ/HTTPBIN_8080_TCP"]
    return HttpBinClient("http://0.0.0.0:{port}".format(port=httpbin_port))

    return HttpBinClient()


def test_ip(client):
    """
    """
    res = client.ip()

    assert "origin" in res


def test_ip_repeat(client):
    """
    """
    res = client.ip_repeat()

    for ip in res:
        assert "origin" in ip


def test_uuid(client):
    """
    """
    res = client.uuid()

    assert "uuid" in res


def test_user_agent(client):
    """
    """
    res = client.user_agent()

    assert res['user-agent'] == 'decorest/{v}'.format(v=decorest_version)


def test_headers(client):
    """
    """
    res = client.headers(header={'A': 'AA', 'B': 'CC'})

    assert res['headers']['User-Agent'] == 'decorest/{v}'.format(
        v=decorest_version)
    assert res['headers']['A'] == 'AA'
    assert res['headers']['B'] == 'CC'

    res = client.headers()

    assert res['headers']['B'] == 'BB'


def test_get(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.get(query=data)

    assert res["args"] == data


def test_post(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.post(data, content='application/json', query=data)

    assert res["args"] == data
    assert res["json"] == data


def test_post_form(client):
    """
    """
    res = client.post_form("value1", "value2", "value3")

    assert res["form"]["key1"] == "value1"
    assert res["form"]["key2"] == "value2"
    assert res["form"]["key3"] == "value3"


def test_post_multipart(client):
    """
    """
    # TODO add multipart decorator
    file = 'tests/testdata/multipart.dat'
    m = MultipartEncoder(
        fields={'test': ('filename', open(file, 'rb'), 'text/plain')}
    )

    res = client.post(None, content=m.content_type, data=m)

    assert res["files"]["test"] == open(file, 'rb').read().decode("utf-8")


def test_patch(client):
    """
    """
    data = "ABCD"
    res = client.patch(data, content="text/plain")

    assert res["data"] == data


def test_put(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.put(data, content="application/json", query=data)

    assert res["args"] == data
    assert res["json"] == data


def test_delete(client):
    """
    """
    data = {"a": "b", "c": "1"}
    client.delete(query=data)


def test_anything(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.anything(data, content="application/json", query=data)

    assert res["args"] == data
    assert res["json"] == data


def test_anything_anything(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.anything_anything(
        "something", data, content="application/json", query=data)

    assert res["args"] == data
    assert res["json"] == data


def test_encoding_utf(client):
    """
    """
    # TODO - add charset decorator


def test_gzip(client):
    """
    """
    res = client.gzip()

    assert json.loads(res)['gzipped'] is True


def test_deflate(client):
    """
    """
    res = client.deflate()

    assert json.loads(res)['deflated'] is True


def test_brotli(client):
    """
    """
    res = client.brotli()

    assert json.loads(res)['brotli'] is True


def test_status(client):
    """
    """
    assert 418 == client.status_code(418)


def test_response_headers(client):
    """
    """
    res = client.response_headers('HTTP', 'BIN')

    assert res['firstName'] == 'HTTP'
    assert res['lastName'] == 'BIN'
    assert res['nickname'] == 'httpbin'


def test_redirect(client):
    """
    """
    res = client.redirect(
        2, on={302: lambda r: 'REDIRECTED'}, allow_redirects=False)

    assert res == 'REDIRECTED'


def test_redirect_to(client):
    """
    """
    res = client.redirect_to('http://httpbin.org',
                             on={302: lambda r: 'REDIRECTED'},
                             allow_redirects=False)

    assert res == 'REDIRECTED'


def test_redirect_to_foo(client):
    """
    """
    res = client.redirect_to_foo('http://httpbin.org', 307,
                                 on={307: lambda r: 'REDIRECTED'},
                                 allow_redirects=False)

    assert res == 'REDIRECTED'


def test_relative_redirect(client):
    """
    """
    res = client.relative_redirect(
        1, on={302: lambda r: r.headers['Location']}, allow_redirects=False)

    assert res == '/get'


def test_absolute_redirect(client):
    """
    """
    res = client.absolute_redirect(
        1, on={302: lambda r: r.headers['Location']}, allow_redirects=False)

    assert res.endswith('/get')


def test_cookies(client):
    """
    """
    jar = cookies.RequestsCookieJar()
    jar.set('cookie1', 'A', path='/cookies')
    jar.set('cookie2', 'B', path='/fruits')
    res = client.cookies(cookies=jar)

    assert res['cookies']['cookie1'] == 'A'
    assert 'cookie2' not in res['cookies']


def test_cookies_set(client):
    """
    """
    res = client.cookies_set(query={"cookie1": "A", "cookie2": "B"})

    assert res["cookies"]["cookie1"] == "A"
    assert res["cookies"]["cookie2"] == "B"


def test_cookies_delete(client):
    """
    """
    client.cookies_set(query={"cookie1": "A", "cookie2": "B"})
    client.cookies_delete(query={"cookie1": None})
    res = client.cookies()

    assert "cookie1" not in res["cookies"]


def test_basic_auth(client):
    """
    """
    res = client.basic_auth(
        'user', 'password', auth=HTTPBasicAuth('user', 'password'))

    assert res['authenticated'] is True


def test_hidden_basic_auth(client):
    """
    """
    res = client.hidden_basic_auth(
        'user', 'password', auth=HTTPBasicAuth('user', 'password'))

    assert res['authenticated'] is True


def test_digest_auth_algorithm(client):
    """
    """
    res = client.digest_auth_algorithm(
        'auth', 'user', 'password', 'MD5',
        auth=HTTPDigestAuth('user', 'password'))

    assert res['authenticated'] is True


def test_digest_auth(client):
    """
    """
    res = client.digest_auth(
        'auth', 'user', 'password', auth=HTTPDigestAuth('user', 'password'))

    assert res['authenticated'] is True


def test_stream_n(client):
    """
    """
    count = 0
    with client.stream_n(5) as r:
        for line in r.iter_lines():
            count += 1

    assert count == 5


def test_delay(client):
    """
    """
    with pytest.raises(ReadTimeout, message="Operation should have timed out"):
        client.delay(5)

    try:
        client.delay(1)
        client.delay(3, timeout=4)
    except ReadTimeout:
        pytest.fail("Operation should not have timed out")


def test_drip(client):
    """
    """
    content = []
    with client.drip(10, 5, 1, 200) as r:
        for b in r.iter_content(chunk_size=1):
            content.append(b)

    assert len(content) == 10


def test_range(client):
    """
    """
    content = []
    with client.range(128, 1, 2, header={"Range": "bytes=10-19"}) as r:
        for b in r.iter_content(chunk_size=2):
            content.append(b)

    assert len(content) == 5


def test_html(client):
    """
    """
    res = client.html(
        on={200: lambda r: (r.headers['content-type'], r.content)})

    assert res[0] == 'text/html; charset=utf-8'
    assert res[1].decode(
        "utf-8").count('<h1>Herman Melville - Moby-Dick</h1>') == 1


def test_robots_txt(client):
    """
    """
    res = client.robots_txt()

    assert "Disallow: /deny" in res


def test_deny(client):
    """
    """
    res = client.deny()

    assert "YOU SHOULDN'T BE HERE" in res


def test_cache(client):
    """
    """
    status_code = client.cache(header={
        'If-Modified-Since': 'Sat, 16 Aug 2015 08:00:00 GMT'},
        on={HttpStatus.ANY: lambda r: r.status_code})

    assert status_code == 304


def test_cache_n(client):
    """
    """
    res = client.cache_n(10)

    assert 'Cache-Control' not in res['headers']


def test_etag(client):
    """
    """
    status_code = client.etag('etag',
                              header={'If-Match': 'notetag'},
                              on={HttpStatus.ANY: lambda r: r.status_code})

    assert status_code == 412

    status_code = client.etag('etag',
                              header={'If-Match': 'etag'},
                              on={HttpStatus.ANY: lambda r: r.status_code})

    assert status_code == 200


def test_bytes(client):
    """
    """
    content = client.stream_bytes(128)

    assert len(content) == 128


def test_stream_bytes(client):
    """
    """
    content = client.stream_bytes(128)

    assert len(content) == 128


def test_links(client):
    """
    """
    html = client.links(10)

    assert html.count('href') == 10 - 1


def test_image(client):
    """
    """
    img = client.image(accept='image/jpeg', on={200: parse_image})

    assert img.format == 'JPEG'

    img = client.image_png()

    assert img.format == 'PNG'

    img = client.image_jpeg()

    assert img.format == 'JPEG'

    img = client.image_webp()

    assert img.format == 'WEBP'


def test_xml(client):
    """
    """
    slideshow = client.xml(on={200: lambda r: ET.fromstring(r.text)})

    assert slideshow.tag == 'slideshow'
