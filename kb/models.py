"""The three shapes everything else passes around."""
from dataclasses import dataclass, field


@dataclass
class SourceDoc:
    """One file or issue from a source system, with who is allowed to read it."""
    id: str             # "drive:1aX9..." or "jira:SERV-101"
    source: str         # "drive" or "jira"
    title: str
    url: str
    updated: str
    text: str
    acl: set[str]       # principals, e.g. {"group:sales", "user:asha@vardhanpumps.in"}


@dataclass(frozen=True)
class Principal:
    """The person asking, built from their SSO token."""
    email: str
    groups: frozenset[str] = field(default_factory=frozenset)
    domain: str = ""

    def principals(self) -> set[str]:
        """Every ACL entry that would let this person in."""
        out = {f"user:{self.email}"} | {f"group:{g}" for g in self.groups}
        if self.domain:
            out.add(f"domain:{self.domain}")
        return out


@dataclass
class Hit:
    chunk_id: int
    doc_id: str
    title: str
    url: str
    text: str
    score: float
