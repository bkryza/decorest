import os
import pytest
import time
import json
import xml.etree.ElementTree as ET
from requests.exceptions import HTTPError

from .petstore_client import PetstoreClient


@pytest.fixture
def client():
    # Give Docker and Swagger Petstore some time to spin up
    time.sleep(5)
    petstore_port = os.environ["SWAGGERAPI/PETSTORE_8080_TCP"]
    return PetstoreClient("http://0.0.0.0:{port}/v2".format(port=petstore_port))


def test_pet_methods(client):

    res = client.find_pet_by_status()
    assert res == []

    res = client.find_pet_by_status_xml()
    assert res.tag == 'pets'

    try:
        res = client.add_pet({
            "name": "lucky",
            "photoUrls": ["http://example.com/lucky.jpg"],
            "status": "available"})
    except HTTPError as e:
        pytest.fail(e.response.text)

    pet_id = res['id']
    res = client.find_pet_by_id(pet_id)
    assert res['name'] == 'lucky'
    assert res['status'] == 'available'

    try:
        res = client.update_pet(json.dumps({
            "id": pet_id,
            "status": "sold"}))
    except HTTPError as e:
        pytest.fail(e.response.text)

    res = client.find_pet_by_id(pet_id)
    assert res['status'] == 'sold'

    try:
        res = client.delete_pet(pet_id)
    except HTTPError as e:
        pytest.fail(e.response.text)

    try:
        res = client.find_pet_by_id(pet_id)
    except HTTPError as e:
        assert e.response.status_code == 404

    assert res == None
