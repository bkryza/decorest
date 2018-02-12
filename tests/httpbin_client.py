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

import io
from PIL import Image
import gzip
import zlib
import brotli
import json
import functools

from decorest import RestClient, HttpStatus
from decorest import GET, POST, PATCH, PUT, DELETE
from decorest import header, query, endpoint, timeout, body, on
from decorest import accept, content, stream
from decorest import decorest_version


def repeatdecorator(f):
    """Example third-party decorator which repeats the call 5 times"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        result = []
        for i in range(5):
            result.append(f(*args, **kwargs))
        return result
    return wrapped


def parse_image(response):
    """Handler for parsing image content and creating image object"""

    with io.BytesIO(response.content) as data:
        with Image.open(data) as img:
            return img

    return None


@header('user-agent', 'decorest/{v}'.format(v=decorest_version))
@accept('application/json')
@endpoint('http://httpbin.org')
class HttpBinClient(RestClient):
    """Client to HttpBin service (httpbin.org)"""

    def __init__(self, endpoint=None):
        super(HttpBinClient, self).__init__(endpoint)

    @GET('ip')
    def ip(self):
        """Returns Origin IP"""

    @repeatdecorator
    @GET('ip')
    def ip_repeat(self):
        """Returns Origin IP repeated n times"""

    @GET('uuid')
    def uuid(self):
        """Returns UUID4"""

    @GET('user-agent')
    def user_agent(self):
        """Returns user-agent"""

    @GET('headers')
    @header('B', 'BB')
    def headers(self):
        """Returns header dict"""

    @GET('get')
    def get(self):
        """Returns GET data"""

    @POST('post')
    @body('post_data')
    def post(self, post_data):
        """Returns POST data"""

    @PATCH('patch')
    @body('patch_data')
    def patch(self, patch_data):
        """Returns PATCH data"""

    @PUT('put')
    @body('put_data', lambda c: json.dumps(c, sort_keys=True, indent=4))
    def put(self, put_data):
        """Returns PUT data"""

    @DELETE('delete')
    def delete(self):
        """Returns DELETE data"""

    @GET('anything')
    @body('content')
    def anything(self, content):
        """Returns request data, including method used"""

    @GET('anything/{anything}')
    @body('content')
    def anything_anything(self, anything, content):
        """Returns request data, including the URL"""

    @GET('encoding/utf8')
    @accept('text/html')
    def encoding_utf8(self):
        """Returns request data, including the URL"""

    @GET('gzip')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def gzip(self):
        """Returns gzip-encoded data"""

    @GET('deflate')
    @content('application/octet-stream')
    @on(200, lambda r: r.content)
    def deflate(self):
        """Returns deflate-encoded data"""

    @GET('brotli')
    @content('application/octet-stream')
    @on(200, lambda r: brotli.decompress(r.content))
    def brotli(self):
        """Returns brotli-encoded data"""

    @GET('status/{code}')
    @on(HttpStatus.ANY, lambda r: r.status_code)
    def status_code(self, code):
        """Returns given HTTP Status code"""

    @GET('response-headers')
    @query('first_name', 'firstName')
    @query('last_name', 'lastName')
    @query('nickname')
    def response_headers(self, first_name, last_name, nickname='httpbin'):
        """Returns given response headers"""

    @GET('redirect/{n}')
    def redirect(self, n):
        """302 Redirects n times"""

    @GET('redirect-to')
    @query('url')
    def redirect_to(self, url):
        """302 Redirects to the foo URL"""

    @GET('redirect-to')
    @query('url')
    @query('code', 'status_code')
    def redirect_to_foo(self, url, code):
        """307 Redirects to the foo URL"""

    @GET('relative-redirect/{n}')
    def relative_redirect(self, n):
        """302 Relative redirects n times"""

    @GET('absolute-redirect/{n}')
    def absolute_redirect(self, n):
        """302 Absolute redirects n times"""

    @GET('cookies')
    def cookies(self):
        """Returns cookie data"""

    @GET('cookies/set')
    def cookies_set(self):
        """Sets one or more simple cookies"""

    @GET('cookies/delete')
    def cookies_delete(self):
        """Deletes one or more simple cookies"""

    @GET('basic-auth/{user}/{passwd}')
    def basic_auth(self, user, passwd):
        """Challenges HTTPBasic Auth"""

    @GET('hidden-basic-auth/{user}/{passwd}')
    def hidden_basic_auth(self, user, passwd):
        """404'd BasicAuth"""

    @GET('digest-auth/{qop}/{user}/{passwd}/{algorithm}/never')
    def digest_auth_algorithm(self, qop, user, passwd, algorithm):
        """Challenges HTTP Digest Auth"""

    @GET('digest-auth/{qop}/{user}/{passwd}')
    def digest_auth(self, qop, user, passwd):
        """Challenges HTTP Digest Auth"""

    @GET('stream/{n}')
    @stream
    def stream_n(self, n):
        """Streams min(n, 100) lines"""

    @GET('delay/{n}')
    @timeout(2)
    def delay(self, n):
        """Delays responding for min(n, 10) seconds"""

    @GET('drip')
    @stream
    @query('numbytes')
    @query('duration')
    @query('delay')
    @query('code')
    def drip(self, numbytes, duration, delay, code):
        """Drips data over a duration after an optional initial delay,
           then (optionally) returns with the given status code"""

    @GET('range/{n}')
    @stream
    @query('duration')
    @query('chunk_size')
    def range(self, n, duration, chunk_size):
        """Streams n bytes, and allows specifying a Range header to select
           Parameterof the data. Accepts a chunk_size and request duration
           parameter"""

    @GET('html')
    @accept('text/html')
    def html(self):
        """Renders an HTML Page"""

    @GET('robots.txt')
    def robots_txt(self):
        """Returns some robots.txt rules"""

    @GET('deny')
    def deny(self):
        """Denied by robots.txt file"""

    @GET('cache')
    def cache(self):
        """Returns 200 unless an If-Modified-Since or If-None-Match header
           is provided, when it returns a 304"""

    @GET('etag/{etag}')
    def etag(self, etag):
        """Assumes the resource has the given etag and responds to
           If-None-Match header with a 200 or 304 and If-Match with a 200
           or 412 as appropriate"""

    @GET('cache/{n}')
    def cache_n(self, n):
        """Sets a Cache-Control header for n seconds"""

    @GET('bytes/{n}')
    def bytes(self, n):
        """Generates n random bytes of binary data, accepts optional seed
           integer parameter"""

    @GET('stream-bytes/{n}')
    def stream_bytes(self, n):
        """Streams n random bytes of binary data in chunked encoding, accepts
           optional seed and chunk_size integer parameters"""

    @GET('links/{n}')
    @accept('text/html')
    def links(self, n):
        """Returns page containing n HTML links"""

    @GET('image')
    def image(self):
        """Returns page containing an image based on sent Accept header"""

    @GET('/image/png')
    @accept('image/png')
    @on(200, parse_image)
    def image_png(self):
        """Returns a PNG image"""

    @GET('/image/jpeg')
    @accept('image/jpeg')
    @on(200, parse_image)
    def image_jpeg(self):
        """Returns a JPEG image"""

    @GET('/image/webp')
    @accept('image/webp')
    @on(200, parse_image)
    def image_webp(self):
        """Returns a WEBP image"""

    @GET('/image/svg')
    @accept('image/svg')
    def image_svg(self):
        """Returns a SVG image"""

    @POST('forms/post')
    @body('forms')
    def forms_post(self, forms):
        """HTML form that submits to /post"""

    @GET('xml')
    @accept('application/xml')
    def xml(self):
        """Returns some XML"""
