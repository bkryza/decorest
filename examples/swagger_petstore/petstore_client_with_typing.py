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
import typing
import xml.etree.ElementTree as ET

from PIL.Image import Image

from decorest import DELETE, GET, POST, PUT
from decorest import HttpStatus, RestClient
from decorest import __version__
from decorest import accept, body, content, endpoint, header, on, query

JsonDictType = typing.Dict[str, typing.Any]


class PetAPI(RestClient):
    """Everything about your Pets."""
    @POST('pet')
    @content('application/json')
    @accept('application/json')
    @body('pet', lambda p: json.dumps(p))
    def add_pet(self, pet: JsonDictType) -> None:
        """Add a new pet to the store."""

    @PUT('pet')
    @body('pet')
    def update_pet(self, pet: JsonDictType) -> None:
        """Update an existing pet."""

    @GET('pet/findByStatus')
    @on(200, lambda r: r.json())
    @on(HttpStatus.ANY, lambda r: r.raise_for_status())
    def find_pet_by_status(self) -> typing.List[JsonDictType]:
        """Find Pets by status."""

    @GET('pet/findByStatus')
    @accept('application/xml')
    @on(200, lambda r: ET.fromstring(r.text))
    def find_pet_by_status_xml(self) -> ET.Element:
        """Find Pets by status."""

    @GET('pet/{pet_id}')
    def find_pet_by_id(self, pet_id: str) -> JsonDictType:
        """Find Pet by ID."""

    @POST('pet/{pet_id}')
    @body('pet', lambda p: json.dumps(p))
    def update_pet_by_id(self, pet_id: str, pet: JsonDictType) -> None:
        """Update a pet in the store with form data."""

    @DELETE('pet/{pet_id}')
    def delete_pet(self, pet_id: str) -> None:
        """Delete a pet."""

    @POST('pet/{pet_id}/uploadImage')
    @body('pet', lambda p: json.dumps(p))
    def upload_pet_image(self, pet_id: str, image: Image) -> None:
        """Upload an image."""


class StoreAPI(RestClient):
    """Access to Petstore orders."""
    @GET('store/inventory')
    def get_inventory(self) -> JsonDictType:
        """Return pet inventories by status."""

    @POST('store/order')
    @body('order', lambda o: json.dumps(o))
    def place_order(self, order: JsonDictType) -> None:
        """Place an order for a pet."""

    @GET('store/order/{order_id}')
    def get_order(self, order_id: str) -> JsonDictType:
        """Find purchase order by ID."""

    @DELETE('store/order/{order_id}')
    def delete_order(self, order_id: str) -> None:
        """Delete purchase order by ID."""


class UserAPI(RestClient):
    """Operations about user."""
    @POST('user')
    @body('user', lambda o: json.dumps(o))
    @on(200, lambda r: True)
    def create_user(self, user: JsonDictType) -> bool:
        """Create user."""

    @POST('user/createWithArray')
    @body('user', lambda o: json.dumps(o))
    def create_users_from_array(self, user: typing.List[JsonDictType]) \
            -> None:
        """Create list of users with given input array."""

    @POST('user/createWithList')
    @body('user', lambda o: json.dumps(o))
    def create_users_from_list(self, user: typing.List[JsonDictType]) \
            -> None:
        """Create list of users with given input array."""

    @GET('user/login')
    @query('username')
    @query('password')
    @on(200, lambda r: r.content)
    def login(self, username: str, password: str) -> JsonDictType:
        """Log user into the system."""

    @GET('user/logout')
    def logout(self) -> JsonDictType:
        """Log out current logged in user session."""

    @GET('user/{username}')
    def get_user(self, username: str) -> JsonDictType:
        """Get user by user name."""

    @PUT('user/{username}')
    @body('user', lambda o: json.dumps(o))
    def update_user(self, username: str, user: JsonDictType) -> JsonDictType:
        """Update user."""

    @DELETE('user/{username}')
    def delete_user(self, username: str) -> None:
        """Delete user."""


@header('user-agent', 'decorest/{v}'.format(v=__version__))
@content('application/json')
@accept('application/json')
@endpoint('http://petstore.example.com')
class PetstoreClientWithTyping(PetAPI, StoreAPI, UserAPI):
    """Swagger Petstore client."""


#
# These checks only validate that typing works, they are not meant
# to be executed
#
client = PetstoreClientWithTyping('http://example.com', backend='requests')

assert client.add_pet({'a': {'b': 'c'}}) is None
assert client.update_pet({'a': {'b': 'c'}}) is None
assert client.find_pet_by_status() == [{'a': {'b': 'c'}}]
assert client.find_pet_by_status_xml() == ET.Element('pet')
assert client.find_pet_by_id('123') == {'a': {'b': 'c'}}
assert client.update_pet_by_id('123', {'a': {'b': 'c'}}) is None
assert client.delete_pet('123') is None
assert client.upload_pet_image('123', Image()) is None
assert client.get_inventory() == {'a': {'b': 'c'}}
assert client.place_order({'a': {'b': 'c'}}) is None
assert client.get_order('a') == {'a': {'b': 'c'}}
assert client.delete_order('a') is None
assert client.create_user({'a': {'b': 'c'}}) is True
assert client.create_users_from_array([{'a': {'b': 'c'}}]) is None
assert client.create_users_from_list([{'a': {'b': 'c'}}]) is None
assert client.login('a', 'b') == {'a': {'b': 'c'}}
assert client.logout() == {'a': {'b': 'c'}}
assert client.get_user('a') == {'a': {'b': 'c'}}
assert client.update_user('a', {'a': {'b': 'c'}}) == {'a': {'b': 'c'}}
assert client.delete_user('a') is None
