"""Log in as one user and print what's inside the access token Keycloak gave the app.

python demo/show_token.py asha
"""
import json
import sys

import jwt
from playwright.sync_api import sync_playwright

from two_users import APP, login

with sync_playwright() as p:
    page = p.chromium.launch().new_context().new_page()
    login(page, sys.argv[1])
    token = next(c["value"] for c in page.context.cookies() if c["name"] == "kb_token")

print(f"token: {token[:40]}...  ({len(token)} characters)\n")
print("header:", jwt.get_unverified_header(token))
claims = jwt.decode(token, options={"verify_signature": False})  # just to look; the app verifies it
keep = ["iss", "aud", "azp", "exp", "email", "email_verified", "groups"]
print(json.dumps({k: claims.get(k) for k in keep}, indent=2))
