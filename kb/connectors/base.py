"""What every source has to provide. Add Confluence or SharePoint by writing one more of these."""
from typing import Iterator, Protocol

from kb.models import SourceDoc


class Connector(Protocol):
    name: str

    def documents(self) -> Iterator[SourceDoc]:
        """Yield every document with its text and the principals allowed to read it."""
        ...
