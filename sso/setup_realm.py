"""Create the 'vardhan' realm in Keycloak: groups, users, and the kb-app OIDC client.
Safe to run twice. Writes the client secret into .env (never printed).

python sso/setup_realm.py
"""
import json
import os
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
KC = f"http://localhost:{os.environ['KEYCLOAK_PORT']}"
APP = os.environ["APP_URL"]
REALM = "vardhan"
SEED = json.loads((ROOT / "sso" / "demo_users.json").read_text())


def admin() -> httpx.Client:
    tok = httpx.post(f"{KC}/realms/master/protocol/openid-connect/token", data={
        "grant_type": "password", "client_id": "admin-cli",
        "username": "admin", "password": os.environ["KEYCLOAK_ADMIN_PASSWORD"]}, timeout=60).json()["access_token"]
    return httpx.Client(base_url=f"{KC}/admin/realms", headers={"Authorization": f"Bearer {tok}"},
                        timeout=60)


def create(api: httpx.Client, path: str, body: dict, what: str) -> None:
    r = api.post(path, json=body)
    status = "created" if r.status_code == 201 else "exists" if r.status_code == 409 else r.text
    print(f"{what:<40} {status}")


def client_body() -> dict:
    claim = {"access.token.claim": "true", "id.token.claim": "true", "userinfo.token.claim": "true"}
    return {"clientId": "kb-app", "protocol": "openid-connect", "publicClient": False,
            "standardFlowEnabled": True, "directAccessGrantsEnabled": False,
            "redirectUris": [f"{APP}/callback"], "webOrigins": [APP],
            "attributes": {"pkce.code.challenge.method": "S256", "post.logout.redirect.uris": APP},
            "protocolMappers": [
                {"name": "groups", "protocol": "openid-connect", "protocolMapper": "oidc-group-membership-mapper",
                 "config": {**claim, "full.path": "false", "claim.name": "groups"}},
                {"name": "audience", "protocol": "openid-connect", "protocolMapper": "oidc-audience-mapper",
                 "config": {"included.client.audience": "kb-app", "access.token.claim": "true"}}]}


def save_secret(api: httpx.Client) -> None:
    cid = api.get(f"/{REALM}/clients", params={"clientId": "kb-app"}).json()[0]["id"]
    secret = api.get(f"/{REALM}/clients/{cid}/client-secret").json()["value"]
    env = (ROOT / ".env").read_text()
    env = re.sub(r"^OIDC_CLIENT_SECRET=.*$", f"OIDC_CLIENT_SECRET={secret}", env, flags=re.M)
    (ROOT / ".env").write_text(env)
    print("client secret written to .env")


def main() -> None:
    api = admin()
    create(api, "", {"realm": REALM, "enabled": True, "displayName": "Vardhan Pumps",
                     "accessTokenLifespan": 1800}, f"realm {REALM}")
    for g in SEED["groups"]:
        create(api, f"/{REALM}/groups", {"name": g}, f"group {g}")
    create(api, f"/{REALM}/clients", client_body(), "client kb-app")
    for u in SEED["users"]:
        create(api, f"/{REALM}/users", {
            "username": u["username"], "email": u["email"], "emailVerified": True, "enabled": True,
            "firstName": u["first"], "lastName": u["last"], "groups": [f"/{g}" for g in u["groups"]],
            "credentials": [{"type": "password", "value": u["password"], "temporary": False}]},
            f"user {u['username']} {u['groups']}")
    save_secret(api)


if __name__ == "__main__":
    main()
