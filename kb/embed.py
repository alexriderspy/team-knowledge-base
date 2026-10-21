"""A small local embedding model, loaded once."""
import logging
from functools import lru_cache

import numpy as np

logging.getLogger("torch.distributed.elastic.multiprocessing.redirects").setLevel(logging.ERROR)
from sentence_transformers import SentenceTransformer  # noqa: E402
from transformers.utils import logging as hf_logging  # noqa: E402

from kb.config import settings

# bge models were trained with this instruction in front of search queries (not in front of documents)
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def model() -> SentenceTransformer:
    hf_logging.disable_progress_bar()
    return SentenceTransformer(settings.embed_model, device="cpu")


def embed_docs(texts: list[str]) -> np.ndarray:
    return model().encode(texts, normalize_embeddings=True, batch_size=16)


def embed_query(text: str) -> np.ndarray:
    return model().encode(QUERY_PREFIX + text, normalize_embeddings=True)
