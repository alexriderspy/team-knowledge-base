"""The API only answers to tokens our IdP signed, for our app, that haven't expired."""
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app import main
from kb.config import settings

IDP_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
ATTACKER_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


class FakeJWKS:
    def get_signing_key_from_jwt(self, token):
        return type("K", (), {"key": IDP_KEY.public_key()})()


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(type(main.oidc), "jwks", FakeJWKS())
    return TestClient(main.app)


def token(key=IDP_KEY, **over) -> str:
    claims = {"iss": settings.oidc_issuer, "aud": settings.oidc_client_id, "exp": int(time.time()) + 300,
              "email": "rohan.mehta@vardhanpumps.in", "email_verified": True, "groups": ["sales"], **over}
    return jwt.encode(claims, key, algorithm="RS256")


def ask(client, tok=None):
    headers = {"Authorization": f"Bearer {tok}"} if tok else {}
    return client.post("/api/ask", json={"question": "salary bands?"}, headers=headers)


def test_no_token(client):
    assert ask(client).status_code == 401


def test_token_signed_by_someone_else(client):
    assert ask(client, token(ATTACKER_KEY, groups=["hr"])).status_code == 401


def test_token_for_another_app(client):
    assert ask(client, token(aud="some-other-app")).status_code == 401


def test_expired_token(client):
    assert ask(client, token(exp=int(time.time()) - 120)).status_code == 401  # past the 30 s leeway


def test_audit_page_needs_security_group(client):
    r = client.get("/audit", headers={"Authorization": f"Bearer {token()}"})
    assert r.status_code == 403
