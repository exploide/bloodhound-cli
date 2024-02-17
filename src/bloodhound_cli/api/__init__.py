import base64
import datetime
import hashlib
import hmac
import json
import urllib

import requests

from bloodhound_cli.logger import log
from .exceptions import ApiException


class Api:
    """Api class for interacting with the BloodHound API server."""

    _url = None
    """Base URL of the API server."""
    _token_id = None
    """ID of the API token used for authentication."""
    _token_key = None
    """Value of the API token used for authentication."""
    _bearer = None
    """Bearer token as an alternative to the API token for authentication."""


    def __init__(self, url, token_id=None, token_key=None, bearer=None):
        """Create an instance of the Api class and set URL and authentication data.

        Either token_id + token_key or a bearer token needs to be set for authentication
        as long as the Api is not just used for initial login.
        """

        self._url = url
        self._token_id = token_id
        self._token_key = token_key
        self._bearer = bearer


    def _send(self, method, endpoint, data=None):
        """Send a request to the API and return the JSON data from the response."""

        if not self._url:
            raise ApiException("Invalid API URL configured, run the auth subcommand first.")

        endpoint_url = urllib.parse.urljoin(self._url, endpoint)
        headers = {
            "User-Agent": "bhcli",
        }

        if data is not None:
            data = json.dumps(data)
            headers["Content-Type"] = "application/json"

        if self._token_id is not None:
            # compute the authentication MAC according to the BloodHound docs
            digester = hmac.new(self._token_key.encode(), None, hashlib.sha256)
            digester.update(f"{method}{endpoint}".encode())
            digester = hmac.new(digester.digest(), None, hashlib.sha256)
            datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
            digester.update(datetime_formatted[:13].encode())
            digester = hmac.new(digester.digest(), None, hashlib.sha256)
            if data is not None:
                digester.update(data.encode())
            headers["Authorization"] = f"bhesignature {self._token_id}"
            headers["RequestDate"] = datetime_formatted
            headers["Signature"] = base64.b64encode(digester.digest())
        elif self._bearer is not None:
            # use Bearer authentication as an alternative
            headers["Authorization"] = f"Bearer {self._bearer}"

        log.debug("Sending %s request to API endpoint %s", method, endpoint)
        result = requests.request(method=method, url=endpoint_url, headers=headers, data=data, timeout=(3.1, 60))
        log.debug("Received response with code %d:", result.status_code)
        log.debug("%s", result.text)

        if not result.ok:
            if result.status_code == 401:
                raise ApiException("Authentication failure, try to obtain an API token with the auth subcommand first.", result)
            raise ApiException("Received unexpected response from server.", result)

        if result.content:
            return result.json()["data"]
        return {}


    def login(self, username, password):
        """Login to the API with username and password to obtain a Bearer token."""

        endpoint = "/api/v2/login"
        data = {
            "login_method": "secret",
            "secret": password,
            "username": username,
        }
        try:
            return self._send("POST", endpoint, data)
        except ApiException as e:
            if e.response.status_code == 401:
                raise ApiException("Authentication failure, probably the password is wrong.", e.response) from e
            if e.response.status_code == 404:
                raise ApiException("Authentication failure, probably the username does not exist or the URL is incorrect.", e.response) from e
            raise


    def create_token(self, token_name, user_id):
        """Create and return a new API token with a given name for a specific user."""

        endpoint = "/api/v2/tokens"
        data = {
            "token_name": token_name,
            "user_id": user_id,
        }
        return self._send("POST", endpoint, data)


    def upload_status(self, file_upload_id=None):
        """Return status of file upload jobs."""

        endpoint = "/api/v2/file-upload"
        if file_upload_id is not None:
            endpoint += f"?id=eq:{file_upload_id}"
        return self._send("GET", endpoint)


    def start_upload(self):
        """Start a new file upload job."""

        endpoint = "/api/v2/file-upload/start"
        return self._send("POST", endpoint)


    def upload_file(self, file_upload_id, file_content):
        """Upload a file to an existing file upload job."""

        endpoint = f"/api/v2/file-upload/{file_upload_id}"
        return self._send("POST", endpoint, file_content)


    def end_upload(self, file_upload_id):
        """End a file upload job."""

        endpoint = f"/api/v2/file-upload/{file_upload_id}/end"
        return self._send("POST", endpoint)


    def domains(self):
        """Return available domains."""

        endpoint = "/api/v2/available-domains"
        return self._send("GET", endpoint)


    def cypher(self, query, include_properties=True):
        """Run a raw Cypher query."""

        endpoint = "/api/v2/graphs/cypher"
        data = {
            "include_properties": include_properties,
            "query": query,
        }
        return self._send("POST", endpoint, data)
