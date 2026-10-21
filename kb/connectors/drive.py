"""Google Drive connector. It only talks to `service`, which has the googleapiclient shape:

    service.files().list(...).execute()
    service.permissions().list(fileId=...).execute()
    service.files().export(fileId=..., mimeType="text/plain").execute()

Locally `service` is FixtureDrive. In production it's googleapiclient.discovery.build("drive", "v3", ...).
"""
import json
from pathlib import Path
from typing import Any, Iterator

from kb.models import SourceDoc


def drive_acl(permissions: list[dict], company_domain: str) -> set[str]:
    """Turn Drive sharing settings into our principals."""
    acl = set()
    for p in permissions:
        if p["type"] == "user":
            acl.add(f"user:{p['emailAddress'].lower()}")
        elif p["type"] == "group":
            acl.add(f"group:{p['emailAddress'].split('@')[0].lower()}")
        elif p["type"] == "domain":
            acl.add(f"domain:{p['domain'].lower()}")
        elif p["type"] == "anyone":
            acl.add(f"domain:{company_domain}")  # anyone with the link: fine for any employee
    return acl


class DriveConnector:
    name = "drive"

    def __init__(self, service: Any, company_domain: str):
        self.service, self.domain = service, company_domain

    def documents(self) -> Iterator[SourceDoc]:
        page_token = None
        while True:
            resp = self.service.files().list(
                q="mimeType='application/vnd.google-apps.document' and trashed=false",
                fields="nextPageToken, files(id, name, modifiedTime, webViewLink)",
                pageToken=page_token).execute()
            for f in resp["files"]:
                perms = self.service.permissions().list(
                    fileId=f["id"], fields="permissions(type, role, emailAddress, domain)").execute()
                text = self.service.files().export(fileId=f["id"], mimeType="text/plain").execute()
                yield SourceDoc(id=f"drive:{f['id']}", source="drive", title=f["name"], url=f["webViewLink"],
                                updated=f["modifiedTime"], text=text.decode(),
                                acl=drive_acl(perms["permissions"], self.domain))
            page_token = resp.get("nextPageToken")
            if not page_token:
                break


class _Call:
    def __init__(self, result: Any):
        self.result = result

    def execute(self) -> Any:
        return self.result


class FixtureDrive:
    """Serves data/fixtures/drive the way the Drive v3 API would."""

    def __init__(self, root: Path):
        self.root = root
        self.files_json = json.loads((root / "files.json").read_text())["files"]

    def files(self) -> "FixtureDrive":
        return self

    def permissions(self) -> "_Permissions":
        return _Permissions(self.files_json)

    def list(self, **_: Any) -> _Call:
        keep = ("id", "name", "modifiedTime", "webViewLink")
        return _Call({"files": [{k: f[k] for k in keep} for f in self.files_json]})

    def export(self, fileId: str, mimeType: str) -> _Call:
        return _Call((self.root / "content" / f"{fileId}.txt").read_bytes())


class _Permissions:
    def __init__(self, files: list[dict]):
        self.by_id = {f["id"]: f["permissions"] for f in files}

    def list(self, fileId: str, **_: Any) -> _Call:
        return _Call({"permissions": self.by_id[fileId]})
