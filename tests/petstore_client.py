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
from decorest import GET, POST, PUT, DELETE
from decorest import header, query, auth, on, body, accept, content
import xml.etree.ElementTree as ET
import json

from requests.auth import HTTPBasicAuth, HTTPDigestAuth

# Default authentication method for all calls
@auth(HTTPBasicAuth('user', 'password'))
# Provide common headers to all methods
@header('user-agent', 'decorest /0.0.1')
# Simply inherit your client from decorest.RestClient
class PetstoreClient(RestClient):
    def __init__(self, endpoint = None):
        super(PetstoreClient, self).__init__(endpoint)

    @POST('pet')
    @header('content-type', 'application/json')
    @header('accept', 'application/json')
    @body('pet', lambda p: json.dumps(p))
    def add_pet(self, pet):
        """Add a new pet to the store"""

    @PUT('pet')
    @body('pet')
    def update_pet(self, pet):
        """Update an existing pet"""

    @GET('pet/findByStatus')
    # This is the default handler for json content
    @on(200, lambda r: r.json())
    # This is also default
    @on(404, lambda r: r.raise_for_status())
    def find_pet_by_status(self):
        """Finds Pets by status"""

    @GET('pet/findByStatus')
    @accept('application/xml')
    # Automatically return ElementTree from XML content
    @on(200, lambda r: ET.fromstring(r.text))
    def find_pet_by_status_xml(self):
        """Finds Pets by status"""

    @GET('pet/{pet_id}')
    def find_pet_by_id(self, pet_id):
        """Find Pet by ID"""

    @POST('pet/{pet_id}')
    def update_pet_by_id(self, pet_id):
        """Updates a pet in the store with form data"""

    @DELETE('pet/{pet_id}')
    def delete_pet(self, pet_id):
        """Deletes a pet"""

    @POST('pet/{pet_id}/uploadImage')
    # Authenticate only to this method differently
    @auth(HTTPDigestAuth('user', 'password'))
    def upload_pet_image(self, pet_id, image):
        """uploads an image"""
