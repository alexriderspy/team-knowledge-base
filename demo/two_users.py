"""Log in through Keycloak as different people, ask the same question, and screenshot what each one sees.

python demo/two_users.py      (needs Keycloak and the app running, and Playwright installed)
"""
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
APP = os.environ["APP_URL"]
SHOTS = ROOT / "media" / "screenshots"
USERS = {u["username"]: u for u in json.loads((ROOT / "sso" / "demo_users.json").read_text())["users"]}
QUESTION = "What's the latest on the Shree Agro VS-200 order?"


def login(page: Page, username: str, shot: str | None = None) -> None:
    page.goto(APP)                                  # the app redirects to Keycloak's login page
    page.wait_for_selector("#username")
    page.fill("#username", username)
    page.fill("#password", USERS[username]["password"])
    if shot:
        page.screenshot(path=SHOTS / shot)
    page.click("#kc-login")
    page.wait_for_url(f"{APP}/")                    # ...and Keycloak sends us back with a code


def ask(page: Page, question: str, shot: str) -> str:
    page.fill("#q", question)
    page.click("button")
    page.wait_for_selector(".card:not(.muted)", timeout=180_000)
    page.screenshot(path=SHOTS / shot)
    return page.inner_text(".card")


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for i, (user, question) in enumerate([("asha", QUESTION), ("rohan", QUESTION),
                                              ("rohan", "What is the salary band for a senior service engineer?"),
                                              ("meera", "What is the salary band for a senior service engineer?")], 1):
            page = browser.new_context(viewport={"width": 1920, "height": 1080}).new_page()
            login(page, user, shot="01_keycloak_login.png" if i == 1 else None)
            print(f"--- {user} {USERS[user]['groups']}: {question}\n{ask(page, question, f'0{i + 1}_{user}_answer.png')}\n")
            page.context.close()
        page = browser.new_context(viewport={"width": 1920, "height": 1080}).new_page()
        login(page, "priya")
        page.goto(f"{APP}/audit")
        page.screenshot(path=SHOTS / "06_audit_log.png")
        browser.close()


if __name__ == "__main__":
    main()
