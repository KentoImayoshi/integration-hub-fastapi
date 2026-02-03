from typing import Dict, Type
from .base import Connector
from .echo import EchoConnector
from .spacex_latest_launch import SpaceXLatestLaunchConnector

_REGISTRY: Dict[str, Type[Connector]] = {
    EchoConnector.name: EchoConnector,
    SpaceXLatestLaunchConnector.name: SpaceXLatestLaunchConnector,
}


def get_connector(name: str) -> Connector:
    """Resolve a connector instance by name."""
    cls = _REGISTRY.get(name)
    if not cls:
        raise ValueError(f"Unknown connector: {name}")
    return cls()


def list_connectors() -> list[str]:
    """Return available connector names."""
    return sorted(_REGISTRY.keys())


def connector_exists(name: str) -> bool:
    """Return True if a connector name exists in the registry."""
    return name in _REGISTRY
