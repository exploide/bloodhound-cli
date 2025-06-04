import base64
import datetime
import hashlib
import hmac
import json
import time
import urllib

import requests

from bloodhound_cli import cypher
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


    def _send(self, method, endpoint, data=None, content_type="application/json"):
        """Send a request to the API and return the JSON data from the response."""

        if not self._url:
            raise ApiException("Invalid API URL configured, run the auth subcommand first.")

        endpoint_url = urllib.parse.urljoin(self._url, endpoint)
        headers = {
            "User-Agent": "bhcli",
        }

        if data is not None:
            if isinstance(data, (dict, list)):
                data = json.dumps(data).encode()
            headers["Content-Type"] = content_type

        if self._token_id is not None:
            # compute the authentication MAC according to the BloodHound docs
            digester = hmac.new(self._token_key.encode(), None, hashlib.sha256)
            digester.update(f"{method}{endpoint}".encode())
            digester = hmac.new(digester.digest(), None, hashlib.sha256)
            datetime_formatted = datetime.datetime.now().astimezone().isoformat("T")
            digester.update(datetime_formatted[:13].encode())
            digester = hmac.new(digester.digest(), None, hashlib.sha256)
            if data is not None:
                digester.update(data)
            headers["Authorization"] = f"bhesignature {self._token_id}"
            headers["RequestDate"] = datetime_formatted
            headers["Signature"] = base64.b64encode(digester.digest())
        elif self._bearer is not None:
            # use Bearer authentication as an alternative
            headers["Authorization"] = f"Bearer {self._bearer}"

        log.debug("Sending %s request to API endpoint %s", method, endpoint)
        try:
            result = requests.request(method=method, url=endpoint_url, headers=headers, data=data, timeout=(3.1, 60))
        except requests.exceptions.ConnectionError as e:
            log.debug("Got error during connection attempt. Original error is: %s", e)
            raise ApiException(f"Could not connect to API server at '{self._url}'. Make sure BloodHound is running and accessible or run 'bhcli --debug ...' for more information.") from e
        log.debug("Received response with code %d:", result.status_code)
        log.debug("%s", result.text)

        if not result.ok:
            if result.status_code == 401:
                raise ApiException("Authentication failure, try to obtain an API token with the auth subcommand first.", result)
            if result.status_code == 429:
                rate_limit_duration = int(result.headers["X-Rate-Limit-Duration"])
                log.info("Hit request rate limiting. Waiting for %d seconds, then trying again...", rate_limit_duration)
                time.sleep(rate_limit_duration)
                return self._send(method, endpoint, data, content_type)
            raise ApiException("Received unexpected response from server. Run 'bhcli --debug ...' for more information.", result)

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
            if e.response is not None:
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


    def upload_file(self, file_upload_id, file_content, content_type):
        """Upload a file to an existing file upload job."""

        endpoint = f"/api/v2/file-upload/{file_upload_id}"
        return self._send("POST", endpoint, file_content, content_type)


    def end_upload(self, file_upload_id):
        """End a file upload job."""

        endpoint = f"/api/v2/file-upload/{file_upload_id}/end"
        return self._send("POST", endpoint)


    def search(self, name, kind=None):
        """Search for a node by name, optionally restricted to a specific kind."""

        endpoint = f"/api/v2/search?q={urllib.parse.quote_plus(name)}"
        if kind is not None:
            endpoint += f"&type={urllib.parse.quote_plus(kind)}"
        return self._send("GET", endpoint)


    def get_asset_groups(self, tag=None):
        """Get asset groups."""

        endpoint = "/api/v2/asset-groups"
        if tag is not None:
            endpoint += f"?tag=eq:{urllib.parse.quote_plus(tag)}"
        return self._send("GET", endpoint)["asset_groups"]


    def create_asset_group(self, name, tag):
        """Create an asset group."""

        endpoint = "/api/v2/asset-groups"
        data = {
            "name": name,
            "tag": tag,
        }
        return self._send("POST", endpoint, data)


    def add_to_asset_group(self, asset_group_id, sids):
        """Add one or more objects identified by their sid to an asset group."""

        endpoint = f"/api/v2/asset-groups/{asset_group_id}/selectors"
        if isinstance(sids, str):
            sids = [sids]
        data = [
            {
                "action": "add",
                "selector_name": sid,
                "sid": sid,
            }
            for sid in sids
        ]
        return self._send("PUT", endpoint, data)


    def get_saved_queries(self, sort_by=None):
        """Get saved custom queries."""

        endpoint = "/api/v2/saved-queries"
        if sort_by is not None:
            endpoint += f"?sort_by={urllib.parse.quote_plus(sort_by)}"
        return self._send("GET", endpoint)


    def add_saved_query(self, name, query, description=""):
        """Add a custom query."""

        endpoint = "/api/v2/saved-queries"
        data = {
            "name": name,
            "query": query,
            "description": description,
        }
        return self._send("POST", endpoint, data)


    def domains(self, collected=None):
        """Return available domains."""

        endpoint = "/api/v2/available-domains"
        if collected is not None:
            endpoint += f"?collected=eq:{str(collected).lower()}"
        return self._send("GET", endpoint)


    def cypher(self, query, include_properties=True):
        """Run a raw Cypher query."""

        query = query.strip()
        log.debug("Prepared Cypher query: %s", query)
        endpoint = "/api/v2/graphs/cypher"
        data = {
            "include_properties": include_properties,
            "query": query,
        }
        try:
            return self._send("POST", endpoint, data)
        except ApiException as e:
            if e.response is not None and e.response.status_code == 404:
                return { "nodes": {}, "edges": [] }
            raise


    def _objects(self, kind, **kwargs):
        """Return objects of a given kind, filtered by properties given in kwargs."""

        query = f"""MATCH ({cypher.node("n", kind)})
                {cypher.where("n", **kwargs)}
                RETURN n
                """
        return self.cypher(query)["nodes"].values()


    def users(self, **kwargs):
        """Return user objects, filtered by properties given in kwargs."""

        return self._objects("User", **kwargs)


    def computers(self, **kwargs):
        """Return computer objects, filtered by properties given in kwargs."""

        return self._objects("Computer", **kwargs)


    def groups(self, **kwargs):
        """Return group objects, filtered by properties given in kwargs."""

        return self._objects("Group", **kwargs)


    def group_members(self, group_sid, kind=None, indirect_members=True):
        """Return members of a given group (includes indirect members by default)."""

        query = f"""MATCH (g:Group)<-[:MemberOf*1..{"" if indirect_members else "1"}]-({cypher.node("m", kind)})
                {cypher.where("g", objectid=group_sid)}
                RETURN m
                """
        return self.cypher(query)["nodes"].values()


    def root_cas(self, **kwargs):
        """Return RootCA objects, filtered by properties given in kwargs."""

        return self._objects("RootCA", **kwargs)


    def enterprise_cas(self, **kwargs):
        """Return EnterpriseCA objects, filtered by properties given in kwargs."""

        return self._objects("EnterpriseCA", **kwargs)


    def cert_templates(self, **kwargs):
        """Return CertTemplate objects, filtered by properties given in kwargs."""

        return self._objects("CertTemplate", **kwargs)
