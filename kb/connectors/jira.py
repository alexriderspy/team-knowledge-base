"""Jira Cloud connector. It only calls `client.get(path, params)` and reads `.json()`, which is
exactly what an httpx.Client(base_url="https://<site>.atlassian.net", auth=(email, api_token)) does.
Locally `client` is FixtureJira, which answers the same REST paths from JSON files.
"""
import json
from pathlib import Path
from typing import Any, Iterator

from kb.models import SourceDoc


def holders_to_acl(entries: list[dict]) -> set[str]:
    return {f"group:{e['holder']['parameter']}" for e in entries if e["holder"]["type"] == "group"}


class JiraConnector:
    name = "jira"

    def __init__(self, client: Any, site_url: str):
        self.client, self.site = client, site_url

    def project_acl(self, key: str) -> set[str]:
        scheme = self.client.get(f"/rest/api/3/project/{key}/permissionscheme",
                                 params={"expand": "permissions"}).json()
        return holders_to_acl([p for p in scheme["permissions"] if p["permission"] == "BROWSE_PROJECTS"])

    def level_acl(self, level_id: str) -> set[str]:
        members = self.client.get("/rest/api/3/issuesecurityschemes/level/member",
                                  params={"levelId": level_id}).json()
        return holders_to_acl(members["values"])

    def documents(self) -> Iterator[SourceDoc]:
        projects = self.client.get("/rest/api/3/project/search").json()["values"]
        for proj in projects:
            acl = self.project_acl(proj["key"])
            start = 0
            while True:
                page = self.client.get("/rest/api/3/search", params={
                    "jql": f"project = {proj['key']}", "startAt": start, "maxResults": 50,
                    "fields": "summary,description,status,updated,security"}).json()
                for issue in page["issues"]:
                    f = issue["fields"]
                    # a security level narrows the project ACL. Intersecting the groups is stricter
                    # than Jira's "both checks", so it can only ever deny, never over-share.
                    doc_acl = acl & self.level_acl(f["security"]["id"]) if f.get("security") else acl
                    yield SourceDoc(id=f"jira:{issue['key']}", source="jira",
                                    title=f"{issue['key']}: {f['summary']}",
                                    url=f"{self.site}/browse/{issue['key']}", updated=f["updated"],
                                    text=f"{f['summary']}\nStatus: {f['status']['name']}\n{f['description']}",
                                    acl=doc_acl)
                start += len(page["issues"])
                if start >= page["total"]:
                    break


class _Resp:
    def __init__(self, data: Any):
        self.data = data

    def json(self) -> Any:
        return self.data


class FixtureJira:
    """Answers the Jira Cloud REST paths we use from data/fixtures/jira."""

    def __init__(self, root: Path):
        self.issues = json.loads((root / "issues.json").read_text())["issues"]
        self.projects = json.loads((root / "projects.json").read_text())
        self.levels = json.loads((root / "security_levels.json").read_text())

    def get(self, path: str, params: dict | None = None) -> _Resp:
        params = params or {}
        group = lambda g: {"holder": {"type": "group", "parameter": g}}
        if path == "/rest/api/3/project/search":
            return _Resp({"values": [{"key": k, "name": p["name"]} for k, p in self.projects.items()]})
        if path.endswith("/permissionscheme"):
            key = path.split("/")[-2]
            return _Resp({"id": 1, "name": f"{key} scheme", "permissions": [
                {"permission": "BROWSE_PROJECTS", **group(g)} for g in self.projects[key]["browse_groups"]]})
        if path == "/rest/api/3/issuesecurityschemes/level/member":
            return _Resp({"values": [group(g) for g in self.levels[params["levelId"]]["groups"]]})
        if path == "/rest/api/3/search":
            key = params["jql"].split("=")[1].strip()
            hits = [i for i in self.issues if i["fields"]["project"]["key"] == key]
            start, size = params.get("startAt", 0), params.get("maxResults", 50)
            return _Resp({"issues": hits[start:start + size], "startAt": start, "maxResults": size, "total": len(hits)})
        raise ValueError(f"fixture has no route for {path}")
