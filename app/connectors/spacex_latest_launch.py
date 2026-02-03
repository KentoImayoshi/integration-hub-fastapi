from typing import Any, Dict
import httpx

from .base import Connector


class SpaceXLatestLaunchConnector(Connector):
    name = "spacex_latest_launch"

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch the latest SpaceX launch from the public SpaceX API (v5).

        Payload supports:
        - timeout_seconds (optional): float/int
        """
        timeout_seconds = float(payload.get("timeout_seconds", 10))

        url = "https://api.spacexdata.com/v5/launches/latest"
        with httpx.Client(timeout=timeout_seconds) as client:
            r = client.get(url)
            r.raise_for_status()
            data = r.json()

        return {
            "source": "spacex",
            "endpoint": "v5/launches/latest",
            "name": data.get("name"),
            "date_utc": data.get("date_utc"),
            "success": data.get("success"),
            "details": data.get("details"),
            "id": data.get("id"),
        }
