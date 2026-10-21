"""One question, end to end: retrieve with permissions, answer, write the audit row."""
import time

from kb.answer import Answer, answer
from kb.audit import AuditLog
from kb.models import Principal
from kb.retrieve import retrieve
from kb.store import Store


def ask(store: Store, audit: AuditLog, user: Principal, question: str) -> tuple[Answer, list[str]]:
    t0 = time.perf_counter()
    r = retrieve(store, user, question)
    ans = answer(question, r.hits)
    audit.log(user, question,
              retrieved=list(dict.fromkeys(h.doc_id for h in r.hits)), denied=r.denied,
              cited=list(dict.fromkeys(h.doc_id for _, h in ans.cited)),
              ms=int((time.perf_counter() - t0) * 1000))
    return ans, r.denied
