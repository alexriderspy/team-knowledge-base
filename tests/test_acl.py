"""Sharing settings from Drive and Jira turn into the right principals."""
from pathlib import Path

from app.auth import principal_from_claims
from kb.connectors.drive import drive_acl
from kb.connectors.jira import FixtureJira, JiraConnector

FIXTURES = Path(__file__).parent.parent / "data" / "fixtures"


def test_drive_permissions_become_principals():
    perms = [{"type": "user", "emailAddress": "Asha.Kulkarni@vardhanpumps.in"},
             {"type": "group", "emailAddress": "sales@vardhanpumps.in"},
             {"type": "domain", "domain": "vardhanpumps.in"}]
    assert drive_acl(perms, "vardhanpumps.in") == {
        "user:asha.kulkarni@vardhanpumps.in", "group:sales", "domain:vardhanpumps.in"}


def test_jira_security_level_narrows_project_access():
    docs = {d.id: d for d in JiraConnector(FixtureJira(FIXTURES / "jira"), "https://x").documents()}
    assert docs["jira:SERV-101"].acl == {"group:engineering", "group:leadership"}
    assert docs["jira:SERV-104"].acl == {"group:leadership"}  # safety level: engineering is out


def test_unverified_email_gets_no_domain_access():
    claims = {"email": "rohan.mehta@vardhanpumps.in", "email_verified": False, "groups": ["sales"]}
    assert principal_from_claims(claims, "vardhanpumps.in").domain == ""
