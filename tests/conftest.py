import os
import tempfile

# tests never touch the real kb.db or its audit log
os.environ["KB_DB"] = os.path.join(tempfile.mkdtemp(), "app.db")

import pytest  # noqa: E402

from kb.ingest import ingest  # noqa: E402
from kb.models import Principal  # noqa: E402
from kb.store import Store  # noqa: E402

D = "vardhanpumps.in"
USERS = {
    "asha": Principal(f"asha.kulkarni@{D}", frozenset({"engineering"}), D),
    "rohan": Principal(f"rohan.mehta@{D}", frozenset({"sales"}), D),
    "meera": Principal(f"meera.iyer@{D}", frozenset({"hr"}), D),
    "vikram": Principal(f"vikram.vardhan@{D}", frozenset({"leadership"}), D),
    "outsider": Principal("someone@gmail.com", frozenset(), ""),
}


@pytest.fixture(scope="session")
def store(tmp_path_factory) -> Store:
    s = Store(tmp_path_factory.mktemp("kb") / "test.db")
    ingest(s)
    return s
