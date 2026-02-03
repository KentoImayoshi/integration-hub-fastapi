from abc import ABC, abstractmethod
from typing import Any, Dict


class Connector(ABC):
    name: str

    @abstractmethod
    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Run the connector and return a JSON-serializable dict."""
        raise NotImplementedError
