"""OpenID Connect login against Keycloak (or Okta, Entra ID, Google: only OIDC_ISSUER changes).

Authorization code flow with PKCE: the browser goes to the IdP, the user logs in there, the IdP sends
back a one-time code, and our server swaps that code for tokens. We never see a password.
"""
import base64
import hashlib
import secrets
from functools import cached_property

import httpx
import jwt

from kb.config import Settings
from kb.models import Principal


def pkce_pair() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    return verifier, challenge


class OIDC:
    def __init__(self, s: Settings):
        self.s = s
        self.redirect_uri = f"{s.app_url}/callback"

    @cached_property
    def meta(self) -> dict:
        """The IdP publishes its endpoints and signing keys at a well-known URL."""
        return httpx.get(f"{self.s.oidc_issuer}/.well-known/openid-configuration").json()

    @cached_property
    def jwks(self) -> jwt.PyJWKClient:
        return jwt.PyJWKClient(self.meta["jwks_uri"])

    def login_url(self, state: str, challenge: str) -> str:
        q = httpx.QueryParams(client_id=self.s.oidc_client_id, response_type="code", scope="openid email",
                              redirect_uri=self.redirect_uri, state=state,
                              code_challenge=challenge, code_challenge_method="S256")
        return f"{self.meta['authorization_endpoint']}?{q}"

    def exchange(self, code: str, verifier: str) -> dict:
        r = httpx.post(self.meta["token_endpoint"], data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": self.redirect_uri,
            "client_id": self.s.oidc_client_id, "client_secret": self.s.oidc_client_secret,
            "code_verifier": verifier})
        r.raise_for_status()
        return r.json()

    def verify(self, token: str) -> dict:
        """Check the signature, issuer, audience and expiry. Any failure raises jwt.PyJWTError."""
        key = self.jwks.get_signing_key_from_jwt(token).key
        # leeway: the IdP's clock and ours are never exactly in sync, allow 30 seconds either way
        return jwt.decode(token, key, algorithms=["RS256"], audience=self.s.oidc_client_id,
                          issuer=self.s.oidc_issuer, leeway=30)

    def logout_url(self) -> str:
        q = httpx.QueryParams(client_id=self.s.oidc_client_id, post_logout_redirect_uri=self.s.app_url)
        return f"{self.meta['end_session_endpoint']}?{q}"


def principal_from_claims(claims: dict, company_domain: str) -> Principal:
    email = claims["email"].lower()
    domain = email.split("@")[1]
    # only a verified company email counts for "shared with everyone at vardhanpumps.in"
    in_company = claims.get("email_verified") is True and domain == company_domain
    return Principal(email=email, groups=frozenset(claims.get("groups", [])),
                     domain=domain if in_company else "")
