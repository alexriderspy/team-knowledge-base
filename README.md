# Team knowledge base: Drive + Jira search with SSO and per-user permissions

Ask a question in plain English and get an answer from the company's Google Drive docs and Jira issues,
with citations. Everyone logs in with SSO, and **each person only gets answers from documents they're
already allowed to open**. Every question is written to an audit log: who asked, what was retrieved,
and what was denied.

Built for a made-up company, Vardhan Pumps and Services (Pune). Everything runs locally:

| Piece | Here | In production |
|---|---|---|
| SSO | Keycloak in Docker (OIDC) | Okta / Entra ID / Google Workspace: change `OIDC_ISSUER` |
| Google Drive | `FixtureDrive`, same shape as the Drive v3 client | `googleapiclient.discovery.build("drive", "v3", credentials=...)` |
| Jira | `FixtureJira`, answers the same Jira Cloud REST paths | `httpx.Client(base_url="https://<site>.atlassian.net", auth=(email, token))` |
| LLM | qwen2.5:7b on Ollama | any OpenAI-compatible API: change `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` |
| Embeddings | BAAI/bge-small-en-v1.5, local | same |

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium            # only for the demo scripts
cp .env.example .env                   # pick two free ports, set an admin password
ollama pull qwen2.5:7b

python data/make_fixtures.py           # Drive files + Jira issues with their sharing settings
docker compose up -d                   # Keycloak
python sso/setup_realm.py              # realm, groups, users, the kb-app client (secret goes into .env)
python -m kb.ingest                    # chunk, embed, store with ACLs
uvicorn app.main:app --port $APP_PORT  # then open APP_URL and log in as a demo user
```

Demo users and their groups are in `sso/demo_users.json` (local demo accounts only).

```bash
python -m kb.ask --email asha.kulkarni@vardhanpumps.in --groups engineering "What's the latest on the Shree Agro VS-200 order?"
python demo/two_users.py               # logs in as several users through Keycloak, screenshots each answer
pytest -m "not llm"                    # ACLs, retrieval leaks, forged tokens (fast)
pytest -m llm                          # the same leak checks through the real LLM answer
```

## How permissions work

1. Each connector turns the source's sharing settings into principals: `user:<email>`, `group:<name>`,
   `domain:<company domain>`. Drive "anyone with the link" counts as the company domain. A Jira issue
   security level is intersected with the project's browse groups.
2. Those principals are stored next to every chunk (`acl` table).
3. At query time the user's principals come from their verified SSO token (email + `groups` claim), and
   the SQL query only scores chunks whose document shares a principal with them. The LLM never sees the rest.
4. Every hit is checked again in Python before it reaches the prompt.
5. Forbidden documents that matched the question are recorded by id in the audit log, never shown.

Group names must match across the IdP, Drive and Jira. In a real company that's done by syncing groups
from the IdP to both (SCIM). Permissions are copied at ingest time, so re-run the sync often
(Drive's changes API and Jira's `updated >= -15m` JQL make it incremental).

## Layout

```
data/make_fixtures.py     Drive + Jira fixture data, shaped like the real APIs
sso/setup_realm.py        Keycloak realm, groups, users, OIDC client
kb/connectors/            drive.py, jira.py: source -> SourceDoc with ACL
kb/ingest.py              chunk + embed + store
kb/store.py               SQLite: documents, chunks, vectors, acl; permission-filtered search
kb/retrieve.py            permission-aware retrieval + denied list
kb/answer.py              grounded answer with [n] citations
kb/audit.py               append-only audit log
app/auth.py               OIDC login (code flow + PKCE), token verification
app/main.py               FastAPI app + UI
tests/                    ACL mapping, retrieval leaks, LLM leaks, auth
```
