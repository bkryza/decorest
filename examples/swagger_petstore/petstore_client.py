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
"""
Example decorest based client to Swagger Petstore sample service.

    http://petstore.swagger.io/

"""

import json
import xml.etree.ElementTree as ET

from decorest import DELETE, GET, HEAD, POST, PUT
from decorest import HttpStatus, RestClient
from decorest import __version__
from decorest import accept, body, content, endpoint, header, on, query


class PetAPI(RestClient):
    """Everything about your Pets."""
    @POST('pet')
    @content('application/json')
    @accept('application/json')
    @body('pet', lambda p: json.dumps(p))
    def add_pet(self, pet):
        """Add a new pet to the store."""

    @PUT('pet')
    @body('pet')
    def update_pet(self, pet):
        """Update an existing pet."""

    @GET('pet/findByStatus')
    @on(200, lambda r: r.json())
    @on(HttpStatus.ANY, lambda r: r.raise_for_status())
    def find_pet_by_status(self):
        """Find Pets by status."""

    @GET('pet/findByStatus')
    @accept('application/xml')
    @on(200, lambda r: ET.fromstring(r.text))
    def find_pet_by_status_xml(self):
        """Find Pets by status."""

    @GET('pet/{pet_id}')
    def find_pet_by_id(self, pet_id):
        """Find Pet by ID."""

    @HEAD('pet/{pet_id}')
    def head_find_pet(self, pet_id):
        """Head find Pet by ID."""

    @POST('pet/{pet_id}')
    def update_pet_by_id(self, pet_id):
        """Update a pet in the store with form data."""

    @DELETE('pet/{pet_id}')
    def delete_pet(self, pet_id):
        """Delete a pet."""

    @POST('pet/{pet_id}/uploadImage')
    def upload_pet_image(self, pet_id, image):
        """Upload an image."""


class StoreAPI(RestClient):
    """Access to Petstore orders."""
    @GET('store/inventory')
    def get_inventory(self):
        """Return pet inventories by status."""

    @POST('store/order')
    @body('order', lambda o: json.dumps(o))
    def place_order(self, order):
        """Place an order for a pet."""

    @GET('store/order/{order_id}')
    def get_order(self, order_id):
        """Find purchase order by ID."""

    @DELETE('store/order/{order_id}')
    def delete_order(self, order_id):
        """Delete purchase order by ID."""


class UserAPI(RestClient):
    """Operations about user."""
    @POST('user')
    @body('user', lambda o: json.dumps(o))
    @on(200, lambda r: True)
    def create_user(self, user):
        """Create user."""

    @POST('user/createWithArray')
    @body('user', lambda o: json.dumps(o))
    def create_users_from_array(self, user):
        """Create list of users with given input array."""

    @POST('user/createWithList')
    @body('user', lambda o: json.dumps(o))
    def create_users_from_list(self, user):
        """Create list of users with given input array."""

    @GET('user/login')
    @query('username')
    @query('password')
    @on(200, lambda r: r.content)
    def login(self, username, password):
        """Log user into the system."""

    @GET('user/logout')
    def logout(self):
        """Log out current logged in user session."""

    @GET('user/{username}')
    def get_user(self, username):
        """Get user by user name."""

    @PUT('user/{username}')
    @body('user', lambda o: json.dumps(o))
    def update_user(self, username, user):
        """Update user."""

    @DELETE('user/{username}')
    def delete_user(self, username):
        """Delete user."""


@header('user-agent', 'decorest/{v}'.format(v=__version__))
@content('application/json')
@accept('application/json')
@endpoint('http://petstore.example.com')
class PetstoreClient(PetAPI, StoreAPI, UserAPI):
    """Swagger Petstore client."""
