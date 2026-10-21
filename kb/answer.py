"""Write the answer from the retrieved chunks only, with numbered citations.
LLM_BASE_URL and LLM_MODEL pick the model: Ollama locally, any OpenAI-compatible API in production."""
import re
from dataclasses import dataclass

from openai import OpenAI

from kb.config import settings
from kb.models import Hit

NOT_FOUND = "I couldn't find that in the documents you have access to."

SYSTEM = f"""You are the internal knowledge assistant of Vardhan Pumps and Services.
Answer the question using only the numbered sources. After every fact, cite its source number in
square brackets, like [1]. Keep the answer short. If the sources don't answer the question, reply
exactly: {NOT_FOUND}
Never guess, and never mention any document that isn't in the sources."""

client = OpenAI(base_url=settings.llm_base_url, api_key=settings.llm_api_key)


@dataclass
class Answer:
    text: str
    cited: list[tuple[int, Hit]]  # (source number in the answer, chunk)


def build_prompt(question: str, hits: list[Hit]) -> str:
    sources = "\n\n".join(f"[{i}] {h.title}\n{h.text}" for i, h in enumerate(hits, 1))
    return f"Sources:\n\n{sources}\n\nQuestion: {question}"


def answer(question: str, hits: list[Hit]) -> Answer:
    if not hits:
        return Answer(NOT_FOUND, [])
    resp = client.chat.completions.create(
        model=settings.llm_model, temperature=0,
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": build_prompt(question, hits)}])
    text = resp.choices[0].message.content.strip()
    used = sorted({int(n) for n in re.findall(r"\[(\d+)\]", text) if 1 <= int(n) <= len(hits)})
    if not used:  # no citation means nothing in the sources backs it up
        return Answer(NOT_FOUND, [])
    return Answer(text, [(n, hits[n - 1]) for n in used])
