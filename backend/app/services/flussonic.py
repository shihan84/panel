import requests
from requests.auth import HTTPBasicAuth
from typing import Any, Dict, List

class FlussonicService:
    """
    A service class to interact with the Flussonic Media Server API.
    """
    def __init__(self, server_url: str, username: str, password: str):
        if not server_url.startswith(('http://', 'https://')):
            raise ValueError("Server URL must start with http:// or https://")
        
        self.base_url = server_url.rstrip('/')
        self.auth = HTTPBasicAuth(username, password)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Helper method to make requests to the Flussonic API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, auth=self.auth, timeout=15, **kwargs)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            # Handle HTTP errors (e.g., 401 Unauthorized, 404 Not Found)
            print(f"HTTP error occurred: {http_err} - {response.text}")
            raise
        except requests.exceptions.ConnectionError as conn_err:
            # Handle connection errors (e.g., DNS failure, refused connection)
            print(f"Connection error occurred: {conn_err}")
            raise
        except requests.exceptions.Timeout as timeout_err:
            # Handle request timeout
            print(f"Timeout error occurred: {timeout_err}")
            raise
        except requests.exceptions.RequestException as req_err:
            # Handle other request exceptions
            print(f"An unexpected error occurred: {req_err}")
            raise

    def get_streams(self) -> list:
        """
        Fetches a list of all media streams from the Flussonic server.
        Corresponds to the `/flussonic/api/media` endpoint.
        """
        response_data = self._make_request('GET', '/flussonic/api/media')
        return response_data.get('streams', [])

    def get_traffic_report(self, streams: List[str], start_time: int) -> Dict[str, Any]:
        """
        Fetches traffic reports for a list of streams since a given time.
        Corresponds to GET /flussonic/api/get_traffic_reports
        """
        params = {
            'streams': ','.join(streams),
            'from': start_time
        }
        return self._make_request('GET', '/flussonic/api/get_traffic_reports', params=params)

    def get_stream_config(self, stream_name: str) -> Dict[str, Any]:
        """
        Fetches the full configuration for a specific stream.
        This is a workaround as there is no direct public API to get a single stream's config
        in a simple way other than parsing the full config. This is more reliable.
        """
        all_streams_data = self._make_request('GET', '/flussonic/api/media')
        for stream in all_streams_data.get('streams', []):
            if stream.get('name') == stream_name:
                # The 'config' key holds the editable configuration
                return stream.get('config', {})
        raise ValueError(f"Stream '{stream_name}' not found.")

    def update_stream_config(self, stream_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Updates the configuration for a specific stream using a partial config.
        Corresponds to POST /flussonic/api/save_stream/{name}
        """
        endpoint = f"/flussonic/api/save_stream/{stream_name}"
        return self._make_request('POST', endpoint, json=config)
