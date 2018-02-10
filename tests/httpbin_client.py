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

from decorest import RestClient
from decorest import GET
from decorest import header, query, accept, endpoint


@header('user-agent', 'decorest user agent test')
@accept('application/json')
@endpoint('http://httpbin.org')
class HttpBinClient(RestClient):
    def __init__(self, endpoint = None):
        super(HttpBinClient, self).__init__(endpoint)

    @GET('user-agent')
    def user_agent(self):
        """Returns user-agent"""

    @GET('headers')
    @header('B', 'BB')
    def headers(self):
        """Returns header dict"""

    @GET('response-headers')
    @query('first_name', 'firstName')
    @query('last_name', 'lastName')
    @query('nickname')
    def response_headers(self, first_name, last_name, nickname='httpbin'):
        """Returns given response headers"""
