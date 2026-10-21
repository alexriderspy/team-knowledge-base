"""Permission-aware retrieval: the filter runs before ranking, and is checked again after."""
from dataclasses import dataclass

from kb.embed import embed_query
from kb.models import Hit, Principal
from kb.store import Store

DENIED_MIN_SCORE = 0.55  # a forbidden chunk this close to the question goes in the audit log


@dataclass
class Retrieval:
    hits: list[Hit]      # what the user is allowed to see, best first
    denied: list[str]    # doc ids that matched but the user can't read (ids only, never text)


def retrieve(store: Store, user: Principal, question: str, k: int = 4) -> Retrieval:
    qvec = embed_query(question)
    principals = user.principals()
    hits = store.search(qvec, principals, k)
    # second check, in Python, so a bug in the SQL can't leak a chunk to the LLM
    for h in hits:
        if not store.acl_of(h.doc_id) & principals:
            raise PermissionError(f"retrieval returned {h.doc_id} to {user.email}")
    forbidden = store.search(qvec, principals, k, allowed=False)
    denied = list(dict.fromkeys(h.doc_id for h in forbidden if h.score >= DENIED_MIN_SCORE))
    return Retrieval(hits, denied)
