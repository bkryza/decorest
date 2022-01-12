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
"""Example client for HTTPBin service with typing (http://httpbin.org)."""

import functools
import io
import json
import typing

from PIL import Image

from decorest import DELETE, GET, PATCH, POST, PUT
from decorest import HttpStatus, RestClient
from decorest import __version__, accept, body, content, endpoint, form
from decorest import header, multipart, on, query, stream, timeout

JsonDictType = typing.Dict[str, typing.Any]

F = typing.TypeVar('F', bound=typing.Callable[..., typing.Any])


def repeatdecorator(f: F) -> F:
    """Repeat call 5 times."""
    @functools.wraps(f)
    def wrapped(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        result = []
        for i in range(5):
            result.append(f(*args, **kwargs))
        return result

    return typing.cast(F, wrapped)


def parse_image(response: typing.Any) -> typing.Optional[Image]:
    """Parse image content and create image object."""
    with io.BytesIO(response.content) as data:
        with Image.open(data) as img:
            return img

    return None


@header('user-agent', 'decorest/{v}'.format(v=__version__))
@accept('application/json')
@endpoint('http://httpbin.org')
class HttpBinClientWithTyping(RestClient):
    """Client to HttpBin service (httpbin.org)."""
    @GET('ip')
    def ip(self) -> JsonDictType:
        """Return Origin IP."""

    @repeatdecorator
    @GET('ip')
    def ip_repeat(self) -> typing.List[JsonDictType]:
        """Return Origin IP repeated n times."""

    @GET('uuid')
    def uuid(self) -> JsonDictType:
        """Return UUID4."""

    @GET('user-agent')
    def user_agent(self) -> JsonDictType:
        """Return user-agent."""

    @GET('headers')
    @header('B', 'BB')
    def headers(self) -> JsonDictType:
        """Return header dict."""

    @GET('headers')
    @header('first')
    @header('second_header', 'SecondHeader')
    def headers_in_args(self, first: str, second_header: str) \
            -> JsonDictType:
        """Return header dict."""

    @GET('get')
    def get(self) -> JsonDictType:
        """Return GET data."""

    @POST('post')
    @form('key1')
    @form('key2')
    @form('key3')
    def post_form(self, key1: str, key2: str, key3: str) -> JsonDictType:
        """Return POST form data."""

    @POST('post')
    @body('post_data')
    def post(self, post_data: str) -> JsonDictType:
        """Return POST data."""

    @POST('post')
    @multipart('part1')
    @multipart('part_2', 'part2')
    @multipart('test')
    def post_multipart(self, part1: typing.Any, part_2: typing.Any,
                       test: typing.Any) -> JsonDictType:
        """Return multipart POST data."""

    @PATCH('patch')
    @body('patch_data')
    def patch(self, patch_data: str) -> JsonDictType:
        """Return PATCH data."""

    @PUT('put')
    @body('put_data', lambda c: json.dumps(c, sort_keys=True, indent=4))
    def put(self, put_data: str) -> str:
        """Return PUT data."""

    @DELETE('delete')
    def delete(self) -> JsonDictType:
        """Return DELETE data."""

    @POST('anything')
    @body('something')
    def anything(self, something: typing.Mapping[str, typing.Any]) \
            -> JsonDictType:
        """Return request data, including method used."""

    @POST('anything/{anything}')
    @body('something')
    def anything_anything(self, anything: str,
                          something: typing.Mapping[str, typing.Any]) \
            -> JsonDictType:
        """Return request data, including the URL."""

    @GET('encoding/utf8')
    @accept('text/html')
    def encoding_utf8(self) -> JsonDictType:
        """Return request data, including the URL."""

    @GET('gzip')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def gzip(self) -> JsonDictType:
        """Return gzip-encoded data."""

    @GET('deflate')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def deflate(self) -> JsonDictType:
        """Return deflate-encoded data."""

    @GET('brotli')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def brotli(self) -> JsonDictType:
        """Return brotli-encoded data."""

    @GET('status/{code}')
    @on(HttpStatus.ANY, lambda r: r.status_code)
    def status_code(self, code: int) -> JsonDictType:
        """Return given HTTP Status code."""

    @GET('response-headers')
    @query('first_name', 'firstName')
    @query('last_name', 'lastName')
    @query('nickname')
    def response_headers(self,
                         first_name: str,
                         last_name: str,
                         nickname: str = 'httpbin') -> JsonDictType:
        """Return given response headers."""

    @GET('redirect/{n}')
    def redirect(self, n: int) -> JsonDictType:
        """302 Redirects n times."""

    @GET('redirect-to')
    @query('url')
    def redirect_to(self, url: str) -> JsonDictType:
        """302 Redirects to the foo URL."""

    @GET('redirect-to')
    @query('url')
    @query('code', 'status_code')
    def redirect_to_foo(self, url: str, code: int) -> JsonDictType:
        """307 Redirects to the foo URL."""

    @GET('relative-redirect/{n}')
    def relative_redirect(self, n: int) -> JsonDictType:
        """302 Relative redirects n times."""

    @GET('absolute-redirect/{n}')
    def absolute_redirect(self, n: int) -> JsonDictType:
        """302 Absolute redirects n times."""

    @GET('cookies')
    def cookies(self) -> JsonDictType:
        """Return cookie data."""

    @GET('cookies/set')
    def cookies_set(self) -> JsonDictType:
        """Set one or more simple cookies."""

    @GET('cookies/delete')
    def cookies_delete(self) -> JsonDictType:
        """Delete one or more simple cookies."""

    @GET('basic-auth/{user}/{passwd}')
    def basic_auth(self, user: str, passwd: str) -> JsonDictType:
        """Challenge HTTPBasic Auth."""

    @GET('hidden-basic-auth/{user}/{passwd}')
    def hidden_basic_auth(self, user: str, passwd: str) -> JsonDictType:
        """404'd BasicAuth."""

    @GET('digest-auth/{qop}/{user}/{passwd}/{algorithm}/never')
    def digest_auth_algorithm(self, qop: str, user: str, passwd: str,
                              algorithm: str) -> JsonDictType:
        """Challenge HTTP Digest Auth."""

    @GET('digest-auth/{qop}/{user}/{passwd}')
    def digest_auth(self, qop: str, user: str, passwd: str) -> JsonDictType:
        """Challenge HTTP Digest Auth."""

    @GET('stream/{n}')
    @stream
    def stream_n(self, n: int) -> JsonDictType:
        """Stream min(n, 100) lines."""

    @GET('delay/{n}')
    @timeout(2)
    def delay(self, n: int) -> JsonDictType:
        """Delay responding for min(n, 10) seconds."""

    @GET('drip')
    @stream
    @query('numbytes')
    @query('duration')
    @query('delay')
    @query('code')
    def drip(self, numbytes: int, duration: float, delay: int,
             code: int) -> JsonDictType:
        """Drip data over a duration.

        Drip data over a duration after an optional initial delay, then
        (optionally) Return with the given status code.
        """

    @GET('range/{n}')
    @stream
    @query('duration')
    @query('chunk_size')
    def range(self, n: int, duration: int, chunk_size: int) -> JsonDictType:
        """Stream n bytes.

        Stream n bytes, and allows specifying a Range header to select
        Parameterof the data. Accepts a chunk_size and request duration
        parameter.
        """

    @GET('html')
    @accept('text/html')
    def html(self) -> JsonDictType:
        """Render an HTML Page."""

    @GET('robots.txt')
    def robots_txt(self) -> JsonDictType:
        """Return some robots.txt rules."""

    @GET('deny')
    def deny(self) -> JsonDictType:
        """Denied by robots.txt file."""

    @GET('cache')
    def cache(self) -> JsonDictType:
        """Return 200 unless an If-Modified-Since.

        Return 200 unless an If-Modified-Since or If-None-Match header
        is provided, when it Return a 304.
        """

    @GET('etag/{etag}')
    def etag(self, etag: str) -> JsonDictType:
        """Assume the resource has the given etag.

        Assume the resource has the given etag and responds to
        If-None-Match header with a 200 or 304 and If-Match with a 200
        or 412 as appropriate.
        """

    @GET('cache/{n}')
    def cache_n(self, n: str) -> JsonDictType:
        """Set a Cache-Control header for n seconds."""

    @GET('bytes/{n}')
    def bytes(self, n: str) -> JsonDictType:
        """Generate n random bytes.

        Generate n random bytes of binary data, accepts optional seed
        integer parameter.
        """

    @GET('stream-bytes/{n}')
    def stream_bytes(self, n: str) -> JsonDictType:
        """Stream n random bytes.

        Stream n random bytes of binary data in chunked encoding, accepts
        optional seed and chunk_size integer parameters.
        """

    @GET('links/{n}')
    @accept('text/html')
    def links(self, n: str) -> JsonDictType:
        """Return page containing n HTML links."""

    @GET('image')
    def image(self) -> JsonDictType:
        """Return page containing an image based on sent Accept header."""

    @GET('/image/png')
    @accept('image/png')
    @on(200, parse_image)
    def image_png(self) -> typing.Optional[Image]:
        """Return a PNG image."""

    @GET('/image/jpeg')
    @accept('image/jpeg')
    @on(200, parse_image)
    def image_jpeg(self) -> typing.Optional[Image]:
        """Return a JPEG image."""

    @GET('/image/webp')
    @accept('image/webp')
    @on(200, parse_image)
    def image_webp(self) -> typing.Optional[Image]:
        """Return a WEBP image."""

    @GET('/image/svg')
    @accept('image/svg')
    def image_svg(self) -> typing.Optional[Image]:
        """Return a SVG image."""

    @POST('forms/post')
    @body('forms')
    def forms_post(self, forms: typing.Mapping[str, typing.Any]) \
            -> JsonDictType:
        """HTML form that submits to /post."""

    @GET('xml')
    @accept('application/xml')
    def xml(self) -> str:
        """Return some XML."""


#
# These checks only validate that typing works, they are not meant
# to be executed
#
client = HttpBinClientWithTyping('http://example.com', backend='requests')

assert client.ip() == {'ip': '1.2.3.4'}
assert client.ip_repeat() \
       == [{'ip': '1.2.3.4'}, {'ip': '1.2.3.4'}, {'ip': '1.2.3.4'}]
assert client.uuid() == {'ip': '1.2.3.4'}
assert client.user_agent() == {'ip': '1.2.3.4'}
assert client.headers() == {'ip': '1.2.3.4'}
assert client.headers_in_args('a', 'b') == {'ip': '1.2.3.4'}
assert client.get() == {'ip': '1.2.3.4'}
assert client.post_form('a', 'b', 'c') == {'ip': '1.2.3.4'}
assert client.post('a') == {'ip': '1.2.3.4'}
assert client.post_multipart('a', 'b', {'c', 'd'}) == {'ip': '1.2.3.4'}
assert client.patch('a') == {'ip': '1.2.3.4'}
assert client.put('a') == '"ip": "1.2.3.4"'
assert client.delete() == {'ip': '1.2.3.4'}
assert client.anything({'a': 123}) == {'ip': '1.2.3.4'}
assert client.anything_anything('a', {'b': 123}) == {'ip': '1.2.3.4'}
assert client.encoding_utf8() == {'ip': '1.2.3.4'}
assert client.gzip() == {'ip': '1.2.3.4'}
assert client.deflate() == {'ip': '1.2.3.4'}
assert client.brotli() == {'ip': '1.2.3.4'}
assert client.status_code(100) == {'ip': '1.2.3.4'}
assert client.response_headers('a', 'b') == {'ip': '1.2.3.4'}
assert client.redirect(5) == {'ip': '1.2.3.4'}
assert client.redirect_to('example.com') == {'ip': '1.2.3.4'}
assert client.redirect_to_foo('a', 301) == {'ip': '1.2.3.4'}
assert client.relative_redirect(2) == {'ip': '1.2.3.4'}
assert client.absolute_redirect(1) == {'ip': '1.2.3.4'}
assert client.cookies() == {'ip': '1.2.3.4'}
assert client.cookies_set() == {'ip': '1.2.3.4'}
assert client.cookies_delete() == {'ip': '1.2.3.4'}
assert client.basic_auth('a', 'b') == {'ip': '1.2.3.4'}
assert client.hidden_basic_auth('a', 'b') == {'ip': '1.2.3.4'}
assert client.digest_auth_algorithm('a', 'b', 'c', 'd') == {'ip': '1.2.3.4'}
assert client.digest_auth('a', 'b', 'c') == {'ip': '1.2.3.4'}
assert client.stream_n(2) == {'ip': '1.2.3.4'}
assert client.delay(1) == {'ip': '1.2.3.4'}
assert client.drip(1, 2.2, 2, 3) == {'ip': '1.2.3.4'}
assert client.range(1, 2, 3) == {'ip': '1.2.3.4'}
assert client.html() == {'ip': '1.2.3.4'}
assert client.robots_txt() == {'ip': '1.2.3.4'}
assert client.deny() == {'ip': '1.2.3.4'}
assert client.cache() == {'ip': '1.2.3.4'}
assert client.etag('a') == {'ip': '1.2.3.4'}
assert client.cache_n('a') == {'ip': '1.2.3.4'}
assert client.bytes('a') == {'ip': '1.2.3.4'}
assert client.stream_bytes('a') == {'ip': '1.2.3.4'}
assert client.links('a') == {'ip': '1.2.3.4'}
assert client.image() == {'ip': '1.2.3.4'}
assert client.image_png() == Image.Image()
assert client.image_jpeg() == Image.Image()
assert client.image_webp() == Image.Image()
assert client.image_svg() == Image.Image()
assert client.forms_post({'a': 123}) == {'ip': '1.2.3.4'}
assert client.xml() == '<a>b</a>'
