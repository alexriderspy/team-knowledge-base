"""The web app: SSO login, ask a question, see the answer with citations, and an audit page.

uvicorn app.main:app --port 8000
"""
import secrets
from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.auth import OIDC, pkce_pair, principal_from_claims
from kb.audit import AuditLog
from kb.config import settings
from kb.models import Principal
from kb.service import ask
from kb.store import Store

app = FastAPI(title="Vardhan Pumps knowledge base")
templates = Jinja2Templates(Path(__file__).parent / "templates")
oidc = OIDC(settings)
store, audit = Store(settings.db_path), AuditLog(settings.db_path)
pending: dict[str, str] = {}  # state -> PKCE verifier, for logins in progress
COOKIE = "kb_token"


def current_user(request: Request) -> Principal:
    """Every request proves who it is with a token the IdP signed. No token, no answer."""
    header = request.headers.get("authorization", "")
    token = header.removeprefix("Bearer ") if header.startswith("Bearer ") else request.cookies.get(COOKIE)
    if not token:
        raise HTTPException(401, "not logged in")
    try:
        claims = oidc.verify(token)
    except jwt.PyJWTError as e:
        raise HTTPException(401, f"invalid token: {e}")
    return principal_from_claims(claims, settings.company_domain)


@app.get("/login")
def login() -> RedirectResponse:
    state = secrets.token_urlsafe(16)
    verifier, challenge = pkce_pair()
    pending[state] = verifier
    return RedirectResponse(oidc.login_url(state, challenge))


@app.get("/callback")
def callback(code: str, state: str) -> RedirectResponse:
    verifier = pending.pop(state, None)
    if verifier is None:
        raise HTTPException(400, "unknown or reused login state")
    tokens = oidc.exchange(code, verifier)
    oidc.verify(tokens["access_token"])
    resp = RedirectResponse("/")
    resp.set_cookie(COOKIE, tokens["access_token"], httponly=True, samesite="lax",
                    secure=settings.app_url.startswith("https"), max_age=tokens["expires_in"])
    return resp


@app.get("/logout")
def logout() -> RedirectResponse:
    resp = RedirectResponse(oidc.logout_url())
    resp.delete_cookie(COOKIE)
    return resp


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    try:
        user = current_user(request)
    except HTTPException:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "index.html", {"user": user,
                                      "is_auditor": settings.audit_group in user.groups})


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=500)


@app.post("/api/ask")
def api_ask(q: Question, user: Principal = Depends(current_user)) -> dict:
    ans, _denied = ask(store, audit, user, q.question)  # denied goes to the audit log, never to the user
    return {"answer": ans.text,
            "sources": [{"n": n, "title": h.title, "url": h.url} for n, h in ans.cited]}


@app.get("/audit", response_class=HTMLResponse)
def audit_page(request: Request, user: Principal = Depends(current_user)):
    if settings.audit_group not in user.groups:
        raise HTTPException(403, "audit log is for the security team")
    return templates.TemplateResponse(request, "audit.html", {"user": user, "rows": audit.recent()})
