"""Endpoint guards: a tier is a claim about where traffic goes. Test the claim."""

import pytest

from sovereign.providers.tier2_private_endpoint import BoundaryError, assert_private_host
from sovereign.providers.tier3_self_hosted import EgressError, assert_no_egress


@pytest.mark.parametrize(
    "url",
    [
        "https://acme.privatelink.openai.azure.com",
        "https://gw.privatelink.services.ai.azure.com",
        "https://10.2.0.4",
    ],
)
def test_private_hosts_are_accepted(url):
    assert_private_host(url)


@pytest.mark.parametrize(
    "url",
    ["https://acme.openai.azure.com", "https://api.example.com/v1", "https://8.8.8.8"],
)
def test_public_hosts_are_rejected(url):
    with pytest.raises(BoundaryError):
        assert_private_host(url)


@pytest.mark.parametrize(
    "url", ["http://127.0.0.1:8000/v1", "http://10.0.0.10:8000/v1", "http://vllm.svc:8000/v1"]
)
def test_internal_endpoints_are_accepted(url):
    assert_no_egress(url)


def test_public_self_hosted_endpoint_is_rejected():
    with pytest.raises(EgressError):
        assert_no_egress("https://inference.example.com/v1")
