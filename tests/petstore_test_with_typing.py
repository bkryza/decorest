# -*- coding: utf-8 -*-
#
# Copyright 2018-2023 Bartosz Kryza <bkryza@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import sys
import time
import typing
import xml.etree.ElementTree as ET

from decorest import HTTPErrorWrapper

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../examples")
from swagger_petstore.petstore_client_with_typing import (
    PetstoreClientWithTyping)


def client(backend: typing.Literal['requests', 'httpx']) \
        -> PetstoreClientWithTyping:
    # Give Docker and Swagger Petstore some time to spin up
    time.sleep(2)
    host = "localhost"
    port = os.environ['PETSTORE_8080_TCP_PORT']

    return PetstoreClientWithTyping('http://{host}:{port}/api'.format(
        host=host, port=port),
                                    backend=backend)


client_requests = client('requests')

client_httpx = client('httpx')


def test_pet_methods(client: PetstoreClientWithTyping) -> None:
    res = client.find_pet_by_status()
    assert res == []

    res = client.find_pet_by_status_xml()
    assert res.tag == 'pets'

    try:
        res = client.add_pet(
            {
                'name': 'lucky',
                'photoUrls': ['http://example.com/lucky.jpg'],
                'status': 'available'
            },
            timeout=5)
    except HTTPErrorWrapper as e:
        pass

    pet_id = res['id']
    res = client.find_pet_by_id(pet_id)
    assert res['name'] == 'lucky'
    assert res['status'] == 'available'

    try:
        res = client.update_pet(json.dumps({'id': pet_id, 'status': 'sold'}))
    except HTTPErrorWrapper as e:
        pass

    res = client.find_pet_by_id(pet_id)
    assert res['status'] == 'sold'

    try:
        res = client.delete_pet(pet_id)
    except HTTPErrorWrapper as e:
        pass

    try:
        res = client.find_pet_by_id(pet_id)
    except HTTPErrorWrapper as e:
        assert e.response.status_code == 404

    assert res is None


def test_store_methods(client: PetstoreClientWithTyping) -> None:

    res = client.place_order({
        'petId': 123,
        'quantity': 2,
        'shipDate': '2018-02-13T21:53:00.637Z',
        'status': 'placed',
    })

    assert res['petId'] == 123
    assert res['status'] == 'placed'

    order_id = res['id']
    res = client.get_order(order_id)

    assert res['petId'] == 123
    assert res['status'] == 'placed'

    res = client.get_inventory()
    assert 'available' in res

    client.delete_order(order_id)


def test_user_methods(client: PetstoreClientWithTyping) -> None:

    res = client.create_user({
        'username': 'swagger',
        'firstName': 'Swagger',
        'lastName': 'Petstore',
        'email': 'swagger@example.com',
        'password': 'guess',
        'phone': '001-111-CALL-ME',
        "userStatus": 0
    })

    assert res is True

    res = client.login('swagger', 'petstore')

    assert res.decode("utf-8").startswith('logged in user session:')

    res = client.get_user('swagger')

    assert res['phone'] == '001-111-CALL-ME'

    client.update_user(
        123, {
            'username': 'swagger',
            'firstName': 'Swagger',
            'lastName': 'Petstore',
            'email': 'swagger@example.com',
            'password': 'guess',
            'phone': '001-111-CALL-ME',
            "userStatus": 0
        })

    res = client.get_user('swagger')

    assert res['email'] == 'swagger@example.com'
    assert res['password'] == 'guess'

    client.delete_user('swagger')
