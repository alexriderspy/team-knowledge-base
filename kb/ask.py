"""Ask from the terminal as a given user, to test permissions without a browser.

python -m kb.ask --email asha.kulkarni@vardhanpumps.in --groups engineering "question"
"""
import argparse

from kb.audit import AuditLog
from kb.config import settings
from kb.models import Principal
from kb.retrieve import retrieve
from kb.service import ask
from kb.store import Store

p = argparse.ArgumentParser()
p.add_argument("question")
p.add_argument("--email", required=True)
p.add_argument("--groups", default="")
p.add_argument("--retrieve-only", action="store_true")
a = p.parse_args()

user = Principal(a.email, frozenset(g for g in a.groups.split(",") if g), a.email.split("@")[1])
store = Store(settings.db_path)
print(f"user: {user.email}  groups: {sorted(user.groups)}\n")
if a.retrieve_only:
    r = retrieve(store, user, a.question)
    for h in r.hits:
        print(f"  {h.score:.3f}  {h.title}")
    print(f"\ndenied: {r.denied}")
else:
    ans, denied = ask(store, AuditLog(settings.db_path), user, a.question)
    print(ans.text, "\n")
    for n, h in ans.cited:
        print(f"  [{n}] {h.title}  {h.url}")
    print(f"\ndenied (logged, not shown to the user): {denied}")
