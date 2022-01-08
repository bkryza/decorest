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
import pprint

import httpx
import pytest
import time
import os
import sys
import json

import requests
from requests.structures import CaseInsensitiveDict

from decorest import __version__, HttpStatus, HTTPErrorWrapper
from requests import cookies
from requests.exceptions import ReadTimeout
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from requests_toolbelt.multipart.encoder import MultipartEncoder
import xml.etree.ElementTree as ET

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../examples")
from httpbin.httpbin_client import HttpBinClient, parse_image
from httpx import BasicAuth


def client(backend: str) -> HttpBinClient:
    # Give Docker and HTTPBin some time to spin up
    time.sleep(2)

    host = os.environ["HTTPBIN_HOST"]
    port = os.environ["HTTPBIN_80_TCP_PORT"]

    return HttpBinClient("http://{host}:{port}".format(host=host, port=port),
                         backend=backend)


def basic_auth_client(backend):
    # Give Docker and HTTPBin some time to spin up
    host = os.environ["HTTPBIN_HOST"]
    port = os.environ["HTTPBIN_80_TCP_PORT"]

    if backend == 'requests':
        auth = HTTPBasicAuth('user', 'password')
    else:
        auth = BasicAuth('user', 'password')

    client = HttpBinClient("http://{host}:{port}".format(host=host, port=port),
                           backend=backend,
                           auth=auth)

    return client


# Prepare pytest params
client_requests = client('requests')
basic_auth_client_requests = basic_auth_client('requests')
pytest_params = [pytest.param(client_requests, id='requests')]
pytest_basic_auth_params = [
    pytest.param(client_requests, basic_auth_client_requests, id='requests')
]

client_httpx = client('httpx')
pytest_params.append(pytest.param(client_httpx, id='httpx'))
basic_auth_client_httpx = basic_auth_client('httpx')
pytest_basic_auth_params.append(
    pytest.param(client_httpx, basic_auth_client_httpx, id='httpx'))


@pytest.mark.parametrize("client", pytest_params)
def test_ip(client):
    """
    """
    res = client.ip()

    assert "origin" in res


@pytest.mark.parametrize("client", pytest_params)
def test_ip_repeat(client):
    """
    """
    res = client.ip_repeat()

    for ip in res:
        assert "origin" in ip


@pytest.mark.parametrize("client", pytest_params)
def test_uuid(client):
    """
    """
    res = client.uuid()

    assert "uuid" in res


@pytest.mark.parametrize("client", pytest_params)
def test_user_agent(client):
    """
    """
    res = client.user_agent()

    assert res['user-agent'] == 'decorest/{v}'.format(v=__version__)


@pytest.mark.parametrize("client", pytest_params)
def test_headers(client):
    """
    """
    def ci(d):
        return CaseInsensitiveDict(d)

    # Check
    res = client.headers(header={'A': 'AA', 'B': 'CC'})

    assert ci(
        res['headers'])['User-Agent'] == 'decorest/{v}'.format(v=__version__)
    assert ci(res['headers'])['A'] == 'AA'
    assert ci(res['headers'])['B'] == 'CC'

    # Check with other values
    res = client.headers(header={'A': 'DD', 'B': 'EE'})

    assert ci(res['headers'])['A'] == 'DD'
    assert ci(res['headers'])['B'] == 'EE'

    # Check method default header value
    res = client.headers()

    assert ci(res['headers'])['B'] == 'BB'


@pytest.mark.parametrize("client", pytest_params)
def test_headers_in_args(client):
    """
    """
    # Check passing header value in arguments
    res = client.headers_in_args('1234', 'ABCD')

    ci = CaseInsensitiveDict(res['headers'])

    assert ci['First'] == '1234'
    assert ci['Second-Header'] == 'ABCD'
    assert ci['Third-Header'] == 'Third header value'
    assert ci['Fourth-Header'] == 'WXYZ'
    assert ci['Content-Type'] == 'application/json'
    assert ci['Accept'] == 'application/xml'


@pytest.mark.parametrize("client", pytest_params)
def test_headers_multivalue(client):
    """
    """
    # Check passing header value in arguments
    res = client.headers_multivalue_headers()
    ci = CaseInsensitiveDict(res['headers'])

    assert ci['A'] == '3, 2, 1'
    assert ci['B'] == 'X, Y, Z'

    res = client.headers_multi_accept()
    ci = CaseInsensitiveDict(res['headers'])

    assert ci['accept'] == 'application/xml, application/json, text/plain'


@pytest.mark.parametrize("client", pytest_params)
def test_get(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.get(query=data)

    assert res["args"] == data


@pytest.mark.parametrize("client", pytest_params)
def test_post(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.post(data, content='application/json', query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.parametrize("client", pytest_params)
def test_post_form(client):
    """
    """
    res = client.post_form("value1", "value2", "value3")

    assert res["form"]["key1"] == "value1"
    assert res["form"]["key2"] == "value2"
    assert res["form"]["key3"] == "value3"


@pytest.mark.parametrize("client", pytest_params)
def test_post_multipart(client):
    """
    """
    file = 'tests/testdata/multipart.dat'

    with open(file, 'rb') as f:
        if client._backend() == 'requests':
            m = MultipartEncoder(
                fields={'test': ('filename', f, 'text/plain')})
            res = client.post(None, content=m.content_type, data=m)
        else:
            res = client.post(None,
                              files={'test': ('filename', f, 'text/plain')})

    with open(file, 'rb') as f:
        assert res["files"]["test"] == f.read().decode("utf-8")


@pytest.mark.parametrize("client", pytest_params)
def test_post_multipart_decorators(client):
    """
    """
    file = 'tests/testdata/multipart.dat'

    with open(file, 'rb') as f:
        res = client.post_multipart(b'TEST1', b'TEST2',
                                    ('filename', f, 'text/plain'))

    assert res["files"]["part1"] == 'TEST1'
    assert res["files"]["part2"] == 'TEST2'
    with open(file, 'rb') as f:
        assert res["files"]["test"] == f.read().decode("utf-8")


@pytest.mark.parametrize("client", pytest_params)
def test_patch(client):
    """
    """
    data = "ABCD"
    res = client.patch(data, content="text/plain")

    assert res["data"] == data


@pytest.mark.parametrize("client", pytest_params)
def test_put(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.put(data, content="application/json", query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.parametrize("client", pytest_params)
def test_delete(client):
    """
    """
    data = {"a": "b", "c": "1"}
    client.delete(query=data)


@pytest.mark.parametrize("client", pytest_params)
def test_anything(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.anything(data, content="application/json", query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.parametrize("client", pytest_params)
def test_anything_anything(client):
    """
    """
    data = {"a": "b", "c": "1"}
    res = client.anything_anything("something",
                                   data,
                                   content="application/json",
                                   query=data)

    assert res["args"] == data
    assert res["json"] == data


@pytest.mark.parametrize("client", pytest_params)
def test_encoding_utf(client):
    """
    """
    # TODO - add charset decorator


@pytest.mark.parametrize("client", pytest_params)
def test_gzip(client):
    """
    """
    res = client.gzip()

    assert json.loads(res)['gzipped'] is True


@pytest.mark.parametrize("client", pytest_params)
def test_deflate(client):
    """
    """
    res = client.deflate()

    assert json.loads(res)['deflated'] is True


@pytest.mark.parametrize("client", pytest_params)
def test_brotli(client):
    """
    """
    res = client.brotli()

    assert json.loads(res)['brotli'] is True


@pytest.mark.parametrize("client", pytest_params)
def test_status(client):
    """
    """
    assert 418 == client.status_code(418)


@pytest.mark.parametrize("client", pytest_params)
def test_response_headers(client):
    """
    """
    res = client.response_headers('HTTP', 'BIN')

    assert res['firstName'] == 'HTTP'
    assert res['lastName'] == 'BIN'
    assert res['nickname'] == 'httpbin'


@pytest.mark.parametrize("client", pytest_params)
def test_redirect(client):
    """
    """
    res = client.redirect(2,
                          on={302: lambda r: 'REDIRECTED'},
                          allow_redirects=False)

    assert res == 'REDIRECTED'


@pytest.mark.parametrize("client", pytest_params)
def test_redirect_to(client):
    """
    """
    res = client.redirect_to('http://httpbin.org',
                             on={302: lambda r: 'REDIRECTED'},
                             allow_redirects=False)

    assert res == 'REDIRECTED'


@pytest.mark.parametrize("client", pytest_params)
def test_redirect_to_foo(client):
    """
    """
    res = client.redirect_to_foo('http://httpbin.org',
                                 307,
                                 on={307: lambda r: 'REDIRECTED'},
                                 allow_redirects=False)

    assert res == 'REDIRECTED'


@pytest.mark.parametrize("client", pytest_params)
def test_relative_redirect(client):
    """
    """
    res = client.relative_redirect(1,
                                   on={302: lambda r: r.headers['Location']},
                                   allow_redirects=False)

    assert res == '/get'


@pytest.mark.parametrize("client", pytest_params)
def test_absolute_redirect(client):
    """
    """
    res = client.absolute_redirect(1,
                                   on={302: lambda r: r.headers['Location']},
                                   allow_redirects=False)

    assert res.endswith('/get')


@pytest.mark.parametrize("client", pytest_params)
def test_max_redirect(client):
    """
    """
    with client.session_(max_redirects=1) as s:
        with pytest.raises(HTTPErrorWrapper) as e:
            s.redirect(5, on={302: lambda r: 'REDIRECTED'})

        assert isinstance(e.value.wrapped,
                          (requests.TooManyRedirects, httpx.TooManyRedirects))


@pytest.mark.parametrize("client", pytest_params)
def test_cookies(client):
    """
    """
    jar = cookies.RequestsCookieJar()
    jar.set('cookie1', 'A', path='/cookies')
    jar.set('cookie2', 'B', path='/fruits')
    res = client.cookies(cookies=jar)

    assert res['cookies']['cookie1'] == 'A'
    assert 'cookie2' not in res['cookies']


@pytest.mark.parametrize("client", pytest_params)
def test_cookies_set(client):
    """
    """
    res = client.cookies_set(query={"cookie1": "A", "cookie2": "B"})

    assert res["cookies"]["cookie1"] == "A"
    assert res["cookies"]["cookie2"] == "B"


@pytest.mark.parametrize("client", pytest_params)
def test_cookies_session(client):
    """
    """
    s = client._session()
    res = s.cookies_set(query={"cookie1": "A", "cookie2": "B"})

    assert res["cookies"]["cookie1"] == "A"
    assert res["cookies"]["cookie2"] == "B"

    res = s.cookies()

    assert res["cookies"]["cookie1"] == "A"
    assert res["cookies"]["cookie2"] == "B"

    s._close()


@pytest.mark.parametrize("client", pytest_params)
def test_cookies_session_with_contextmanager(client):
    """
    """
    with client._session() as s:
        s._backend_session.verify = False
        res = s.cookies_set(query={"cookie1": "A", "cookie2": "B"})

        assert res["cookies"]["cookie1"] == "A"
        assert res["cookies"]["cookie2"] == "B"

        res = s.cookies()

        assert res["cookies"]["cookie1"] == "A"
        assert res["cookies"]["cookie2"] == "B"


@pytest.mark.parametrize("client", pytest_params)
def test_cookies_delete(client):
    """
    """
    client.cookies_set(query={"cookie1": "A", "cookie2": "B"})
    client.cookies_delete(query={"cookie1": None})
    res = client.cookies()

    assert "cookie1" not in res["cookies"]


@pytest.mark.parametrize("client,basic_auth_client", pytest_basic_auth_params)
def test_basic_auth(client, basic_auth_client):
    """
    """
    with pytest.raises(HTTPErrorWrapper) as e:
        res = client.basic_auth('user', 'password')

    assert isinstance(e.value, HTTPErrorWrapper)

    res = basic_auth_client.basic_auth('user', 'password')
    assert res['authenticated'] is True


@pytest.mark.parametrize("client,basic_auth_client", pytest_basic_auth_params)
def test_basic_auth_with_session(client, basic_auth_client):
    """
    """
    res = None
    with basic_auth_client._session() as s:
        res = s.basic_auth('user', 'password')

    assert res['authenticated'] is True


@pytest.mark.parametrize("client", pytest_params)
def test_hidden_basic_auth(client):
    """
    """
    res = client.hidden_basic_auth('user',
                                   'password',
                                   auth=HTTPBasicAuth('user', 'password'))

    assert res['authenticated'] is True


@pytest.mark.parametrize("client", pytest_params)
def test_digest_auth_algorithm(client):
    """
    """
    if client._backend() == 'requests':
        auth = HTTPDigestAuth('user', 'password')
    else:
        import httpx
        auth = httpx.DigestAuth('user', 'password')

    res = client.digest_auth_algorithm('auth',
                                       'user',
                                       'password',
                                       'MD5',
                                       auth=auth)

    assert res['authenticated'] is True


@pytest.mark.parametrize("client", pytest_params)
def test_digest_auth(client):
    """
    """
    if client._backend() == 'requests':
        auth = HTTPDigestAuth('user', 'password')
    else:
        import httpx
        auth = httpx.DigestAuth('user', 'password')

    res = client.digest_auth('auth', 'user', 'password', auth=auth)

    assert res['authenticated'] is True


@pytest.mark.parametrize("client", pytest_params)
def test_stream_n(client):
    """
    """
    count = 0
    with client.stream_n(5) as r:
        for line in r.iter_lines():
            count += 1

    assert count == 5


@pytest.mark.parametrize("client", pytest_params)
def test_delay(client):
    """
    """
    with pytest.raises(HTTPErrorWrapper):
        client.delay(5)

    try:
        client.delay(1)
        client.delay(3, timeout=4)
    except HTTPErrorWrapper:
        pytest.fail("Operation should not have timed out")


@pytest.mark.parametrize("client", pytest_params)
def test_drip(client):
    """
    """
    content = []
    with client.drip(10, 5, 1, 200) as r:
        if client._backend() == 'requests':
            for b in r.iter_content(chunk_size=1):
                content.append(b)
        else:
            for b in r.iter_raw():
                content.append(b)

    assert len(content) == 10


@pytest.mark.parametrize("client", pytest_params)
def test_range(client):
    """
    """
    content = []

    with client.range(128, 1, 2, header={"Range": "bytes=10-19"}) as r:
        if client._backend() == 'requests':
            for b in r.iter_content(chunk_size=2):
                content.append(b)
        else:
            for b in r.iter_raw():
                content.append(b)

    assert len(content) == 5


@pytest.mark.parametrize("client", pytest_params)
def test_html(client):
    """
    """
    res = client.html(
        on={200: lambda r: (r.headers['content-type'], r.content)})

    assert res[0] == 'text/html; charset=utf-8'
    assert res[1].decode("utf-8").count(
        '<h1>Herman Melville - Moby-Dick</h1>') == 1


@pytest.mark.parametrize("client", pytest_params)
def test_robots_txt(client):
    """
    """
    res = client.robots_txt()

    assert "Disallow: /deny" in res


@pytest.mark.parametrize("client", pytest_params)
def test_deny(client):
    """
    """
    res = client.deny()

    assert "YOU SHOULDN'T BE HERE" in res


@pytest.mark.parametrize("client", pytest_params)
def test_cache(client):
    """
    """
    status_code = client.cache(
        header={'If-Modified-Since': 'Sat, 16 Aug 2015 08:00:00 GMT'},
        on={HttpStatus.ANY: lambda r: r.status_code})

    assert status_code == 304


@pytest.mark.parametrize("client", pytest_params)
def test_cache_n(client):
    """
    """
    res = client.cache_n(10)

    assert 'Cache-Control' not in res['headers']


@pytest.mark.parametrize("client", pytest_params)
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


@pytest.mark.parametrize("client", pytest_params)
def test_bytes(client):
    """
    """
    content = client.stream_bytes(128)

    assert len(content) == 128


@pytest.mark.parametrize("client", pytest_params)
def test_stream_bytes(client):
    """
    """
    content = client.stream_bytes(128)

    assert len(content) == 128


@pytest.mark.parametrize("client", pytest_params)
def test_links(client):
    """
    """
    html = client.links(10)

    assert html.count('href') == 10 - 1


@pytest.mark.parametrize("client", pytest_params)
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


@pytest.mark.parametrize("client", pytest_params)
def test_xml(client):
    """
    """
    slideshow = client.xml(on={200: lambda r: ET.fromstring(r.text)})

    assert slideshow.tag == 'slideshow'
