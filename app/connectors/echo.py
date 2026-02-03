from typing import Any, Dict
from .base import Connector


class EchoConnector(Connector):
    name = "echo"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Return the same payload back (useful for smoke tests)."""
        return {"echo": payload}
