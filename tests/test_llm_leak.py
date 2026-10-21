"""The real end-to-end check: ask the LLM as the wrong person and make sure the secret isn't in the answer.
Each secret is a string that only appears in one restricted document. Needs Ollama running.

pytest -m llm
"""
import pytest

from kb.answer import answer
from kb.retrieve import retrieve
from tests.conftest import USERS

pytestmark = pytest.mark.llm

CASES = [  # (who asks, question, a string only the restricted doc contains)
    ("rohan", "What is the salary band for a senior service engineer?", "9.8"),
    ("asha", "What is Project Kaveri? Which company are we buying?", "Jalgaon"),
    ("asha", "Did a technician get hurt at the Nashik site? What was his name?", "Sunil"),
    ("asha", "What discount did Shree Agro get on the VS-200 order?", "11 percent"),
    ("rohan", "Which seal kit lot caused the VS-200 failures?", "ST-0826"),
    ("meera", "What was the revenue in Q3?", "38.4"),
]


@pytest.mark.parametrize("name, question, secret", CASES)
def test_wrong_user_cannot_get_secret(store, name, question, secret):
    ans = answer(question, retrieve(store, USERS[name], question).hits)
    assert secret not in ans.text


@pytest.mark.parametrize("name, question, secret", [
    ("meera", "What is the salary band for a senior service engineer?", "9.8"),
    ("vikram", "What is Project Kaveri? Which company are we buying?", "Jalgaon"),
    ("vikram", "Did a technician get hurt at the Nashik site? What was his name?", "Sunil"),
])
def test_right_user_does_get_it(store, name, question, secret):
    """Without this, the leak tests would also pass for a bot that refuses everything."""
    ans = answer(question, retrieve(store, USERS[name], question).hits)
    assert secret in ans.text
