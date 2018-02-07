import pytest

from .httpbin_client import HttpBinClient


@pytest.fixture
def client():
    return HttpBinClient("http://httpbin.org")


def test_user_agent(client):
    """
    GET /user-agent
    """
    res = client.user_agent()
    assert res['user-agent'] == 'decorest user agent test'
