"""Pull every document from every connector, chunk it, embed it and store it with its ACL.

python -m kb.ingest
"""
import re

from kb.config import ROOT, settings
from kb.connectors.base import Connector
from kb.connectors.drive import DriveConnector, FixtureDrive
from kb.connectors.jira import FixtureJira, JiraConnector
from kb.embed import embed_docs
from kb.store import Store


def chunk(title: str, text: str) -> list[str]:
    """One chunk per '## ' section, each starting with the document title so it makes sense alone."""
    parts = [p.strip() for p in re.split(r"\n(?=## )", text) if p.strip()]
    return [f"{title}\n{p}" for p in parts]


def connectors() -> list[Connector]:
    fixtures = ROOT / "data" / "fixtures"
    return [DriveConnector(FixtureDrive(fixtures / "drive"), settings.company_domain),
            JiraConnector(FixtureJira(fixtures / "jira"), "https://vardhanpumps.atlassian.net")]


def ingest(store: Store) -> None:
    for conn in connectors():
        n_docs = n_chunks = 0
        for doc in conn.documents():
            if not doc.acl:
                print(f"  skipped {doc.id}: no one is allowed to read it")
                continue
            chunks = chunk(doc.title, doc.text)
            store.upsert(doc, chunks, embed_docs(chunks))
            n_docs, n_chunks = n_docs + 1, n_chunks + len(chunks)
        print(f"{conn.name}: {n_docs} documents, {n_chunks} chunks")
    print(store.stats(), "\n")
    for title, acl in store.acl_table():
        print(f"  {title[:58]:<60}{acl}")


if __name__ == "__main__":
    ingest(Store(settings.db_path))
