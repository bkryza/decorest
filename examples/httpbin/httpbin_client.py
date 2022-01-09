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
"""Example client for HTTPBin service (http://httpbin.org)."""

import functools
import io
import json

from PIL import Image

from decorest import DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
from decorest import HttpStatus, RestClient
from decorest import __version__, accept, body, content, endpoint, form
from decorest import header, multipart, on, query, stream, timeout


def repeatdecorator(f):
    """Repeat call 5 times."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        result = []
        for i in range(5):
            result.append(f(*args, **kwargs))
        return result

    return wrapped


def parse_image(response):
    """Parse image content and create image object."""
    with io.BytesIO(response.content) as data:
        with Image.open(data) as img:
            return img

    return None


@header('user-agent', 'decorest/{v}'.format(v=__version__))
@accept('application/json')
@endpoint('http://httpbin.org')
class HttpBinClient(RestClient):
    """Client to HttpBin service (httpbin.org)."""
    @GET('ip')
    def ip(self):
        """Return Origin IP."""

    @HEAD('ip')
    @on(200, lambda _: True)
    def head_ip(self):
        """Return Origin IP request headers only."""

    @OPTIONS('ip')
    @on(200, lambda r: r.headers)
    def options_ip(self):
        """Return Origin IP options."""

    @repeatdecorator
    @GET('ip')
    def ip_repeat(self):
        """Return Origin IP repeated n times."""

    @GET('uuid')
    def uuid(self):
        """Return UUID4."""

    @GET('user-agent')
    def user_agent(self):
        """Return user-agent."""

    @GET('headers')
    @header('B', 'BB')
    def headers(self):
        """Return header dict."""

    @GET('headers')
    @header('first')
    @header('second_header', 'Second-Header')
    @header('Third-Header', 'Third header value')
    @header('fourth_header', 'Fourth-Header')
    @content('application/json')
    @accept('application/xml')
    def headers_in_args(self, first, second_header, fourth_header='WXYZ'):
        """Return header dict."""

    @GET('headers')
    @header('A', '1')
    @header('A', '2')
    @header('A', '3')
    @header('B', ['X', 'Y', 'Z'])
    def headers_multivalue_headers(self):
        """Return header dict."""

    @GET('headers')
    @accept('text/plain')
    @accept('application/json')
    @accept('application/xml')
    def headers_multi_accept(self):
        """Return header dict."""

    @GET('headers')
    @header('A', 'a')
    def headers_multivalue_headers_with_override(self, a=['1', '2', '3']):
        """Return header dict."""

    @GET('get')
    def get(self):
        """Return GET data."""

    @POST('post')
    @form('key1')
    @form('key2')
    @form('key3')
    def post_form(self, key1, key2, key3):
        """Return POST form data."""

    @POST('post')
    @body('post_data')
    def post(self, post_data):
        """Return POST data."""

    @POST('post')
    @multipart('part1')
    @multipart('part_2', 'part2')
    @multipart('test')
    def post_multipart(self, part1, part_2, test):
        """Return multipart POST data."""

    @PATCH('patch')
    @body('patch_data')
    def patch(self, patch_data):
        """Return PATCH data."""

    @PUT('put')
    @body('put_data', lambda c: json.dumps(c, sort_keys=True, indent=4))
    def put(self, put_data):
        """Return PUT data."""

    @DELETE('delete')
    def delete(self):
        """Return DELETE data."""

    @POST('anything')
    @body('content')
    def anything(self, content):
        """Return request data, including method used."""

    @POST('anything/{anything}')
    @body('content')
    def anything_anything(self, anything, content):
        """Return request data, including the URL."""

    @GET('encoding/utf8')
    @accept('text/html')
    def encoding_utf8(self):
        """Return request data, including the URL."""

    @GET('gzip')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def gzip(self):
        """Return gzip-encoded data."""

    @GET('deflate')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def deflate(self):
        """Return deflate-encoded data."""

    @GET('brotli')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def brotli(self):
        """Return brotli-encoded data."""

    @GET('status/{code}')
    @on(HttpStatus.ANY, lambda r: r.status_code)
    def status_code(self, code):
        """Return given HTTP Status code."""

    @GET('response-headers')
    @query('first_name', 'firstName')
    @query('last_name', 'lastName')
    @query('nickname')
    def response_headers(self, first_name, last_name, nickname='httpbin'):
        """Return given response headers."""

    @GET('redirect/{n}')
    def redirect(self, n):
        """302 Redirects n times."""

    @GET('redirect-to')
    @query('url')
    def redirect_to(self, url):
        """302 Redirects to the foo URL."""

    @GET('redirect-to')
    @query('url')
    @query('code', 'status_code')
    def redirect_to_foo(self, url, code):
        """307 Redirects to the foo URL."""

    @GET('relative-redirect/{n}')
    def relative_redirect(self, n):
        """302 Relative redirects n times."""

    @GET('absolute-redirect/{n}')
    def absolute_redirect(self, n):
        """302 Absolute redirects n times."""

    @GET('cookies')
    def cookies(self):
        """Return cookie data."""

    @GET('cookies/set')
    def cookies_set(self):
        """Set one or more simple cookies."""

    @GET('cookies/delete')
    def cookies_delete(self):
        """Delete one or more simple cookies."""

    @GET('basic-auth/{user}/{passwd}')
    def basic_auth(self, user, passwd):
        """Challenge HTTPBasic Auth."""

    @GET('hidden-basic-auth/{user}/{passwd}')
    def hidden_basic_auth(self, user, passwd):
        """404'd BasicAuth."""

    @GET('digest-auth/{qop}/{user}/{passwd}/{algorithm}/never')
    def digest_auth_algorithm(self, qop, user, passwd, algorithm):
        """Challenge HTTP Digest Auth."""

    @GET('digest-auth/{qop}/{user}/{passwd}')
    def digest_auth(self, qop, user, passwd):
        """Challenge HTTP Digest Auth."""

    @GET('stream/{n}')
    @stream
    def stream_n(self, n):
        """Stream min(n, 100) lines."""

    @GET('delay/{n}')
    @timeout(2)
    def delay(self, n):
        """Delay responding for min(n, 10) seconds."""

    @GET('drip')
    @stream
    @query('numbytes')
    @query('duration')
    @query('delay')
    @query('code')
    def drip(self, numbytes, duration, delay, code):
        """Drip data over a duration.

        Drip data over a duration after an optional initial delay, then
        (optionally) Return with the given status code.
        """

    @GET('range/{n}')
    @stream
    @query('duration')
    @query('chunk_size')
    def range(self, n, duration, chunk_size):
        """Stream n bytes.

        Stream n bytes, and allows specifying a Range header to select
        Parameterof the data. Accepts a chunk_size and request duration
        parameter.
        """

    @GET('html')
    @accept('text/html')
    def html(self):
        """Render an HTML Page."""

    @GET('robots.txt')
    def robots_txt(self):
        """Return some robots.txt rules."""

    @GET('deny')
    def deny(self):
        """Denied by robots.txt file."""

    @GET('cache')
    def cache(self):
        """Return 200 unless an If-Modified-Since.

        Return 200 unless an If-Modified-Since or If-None-Match header
        is provided, when it Return a 304.
        """

    @GET('etag/{etag}')
    def etag(self, etag):
        """Assume the resource has the given etag.

        Assume the resource has the given etag and responds to
        If-None-Match header with a 200 or 304 and If-Match with a 200
        or 412 as appropriate.
        """

    @GET('cache/{n}')
    def cache_n(self, n):
        """Set a Cache-Control header for n seconds."""

    @GET('bytes/{n}')
    def bytes(self, n):
        """Generate n random bytes.

        Generate n random bytes of binary data, accepts optional seed
        integer parameter.
        """

    @GET('stream-bytes/{n}')
    def stream_bytes(self, n):
        """Stream n random bytes.

        Stream n random bytes of binary data in chunked encoding, accepts
        optional seed and chunk_size integer parameters.
        """

    @GET('links/{n}')
    @accept('text/html')
    def links(self, n):
        """Return page containing n HTML links."""

    @GET('image')
    def image(self):
        """Return page containing an image based on sent Accept header."""

    @GET('/image/png')
    @accept('image/png')
    @on(200, parse_image)
    def image_png(self):
        """Return a PNG image."""

    @GET('/image/jpeg')
    @accept('image/jpeg')
    @on(200, parse_image)
    def image_jpeg(self):
        """Return a JPEG image."""

    @GET('/image/webp')
    @accept('image/webp')
    @on(200, parse_image)
    def image_webp(self):
        """Return a WEBP image."""

    @GET('/image/svg')
    @accept('image/svg')
    def image_svg(self):
        """Return a SVG image."""

    @POST('forms/post')
    @body('forms')
    def forms_post(self, forms):
        """HTML form that submits to /post."""

    @GET('xml')
    @accept('application/xml')
    def xml(self):
        """Return some XML."""
