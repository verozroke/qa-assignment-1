from __future__ import annotations

import logging
from typing import Any

import requests
from requests import Response
from requests.exceptions import RequestException

from config.settings import Settings


class APIClientError(RuntimeError):
    """Raised when an API request fails unexpectedly."""


class APIClient:
    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self.settings = settings
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _build_url(self, path: str) -> str:
        normalized = path if path.startswith("/") else f"/{path}"
        return f"{self.settings.api_base_url}{normalized}"

    def _auth_headers(self, token: str) -> dict[str, str]:
        prefix = self.settings.auth_header_prefix
        auth_value = f"{prefix} {token}".strip() if prefix else token
        return {"Authorization": auth_value}

    def request(
        self,
        method: str,
        path: str,
        expected_status: tuple[int, ...] | None = None,
        **kwargs: Any,
    ) -> Response:
        url = self._build_url(path)
        timeout = kwargs.pop("timeout", self.settings.request_timeout)

        self.logger.info("API request: %s %s", method.upper(), url)
        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                timeout=timeout,
                **kwargs,
            )
        except RequestException as exc:
            self.logger.exception("API request failed: %s %s", method.upper(), url)
            raise APIClientError(f"API request failed for {method.upper()} {url}") from exc

        self.logger.info(
            "API response: %s %s -> %s",
            method.upper(),
            url,
            response.status_code,
        )

        if expected_status is not None and response.status_code not in expected_status:
            message = (
                f"Unexpected status for {method.upper()} {url}. "
                f"Expected {expected_status}, got {response.status_code}. "
                f"Body: {response.text}"
            )
            self.logger.error(message)
            raise APIClientError(message)

        return response

    def authenticate(self, username: str, password: str) -> Response:
        payload = {"username": username, "password": password}
        return self.request("POST", self.settings.api_auth_endpoint, json=payload)

    def create_ticket(self, token: str, payload: dict[str, Any]) -> Response:
        return self.request(
            "POST",
            self.settings.api_tickets_endpoint,
            headers=self._auth_headers(token),
            json=payload,
        )

    def get_ticket(self, token: str, ticket_id: str | int) -> Response:
        path = f"{self.settings.api_tickets_endpoint.rstrip('/')}/{ticket_id}"
        return self.request("GET", path, headers=self._auth_headers(token))

    def close(self) -> None:
        self.session.close()
