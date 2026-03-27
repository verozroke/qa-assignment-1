from __future__ import annotations

import logging
from typing import Any

import pytest
from requests import Response

from config.settings import Settings


class BaseTest:
    logger: logging.Logger
    settings: Settings

    @pytest.fixture(autouse=True)
    def _inject_dependencies(
        self,
        settings: Settings,
        test_logger: logging.Logger,
    ) -> None:
        self.settings = settings
        self.logger = test_logger

    def log_step(self, message: str) -> None:
        self.logger.info("STEP: %s", message)

    def assert_status_code(
        self,
        response: Response,
        expected_codes: tuple[int, ...],
        context: str,
    ) -> None:
        if response.status_code not in expected_codes:
            self.logger.error(
                "%s failed. Expected status in %s but got %s. Body: %s",
                context,
                expected_codes,
                response.status_code,
                response.text,
            )
        assert response.status_code in expected_codes, (
            f"{context} expected status in {expected_codes}, "
            f"got {response.status_code}."
        )

    def parse_json(self, response: Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            self.logger.exception("Expected JSON response but received invalid body.")
            raise AssertionError(f"Response body is not valid JSON: {response.text}") from exc

        if not isinstance(payload, dict):
            self.logger.error(
                "Expected JSON object response but got %s.",
                type(payload).__name__,
            )
            raise AssertionError(
                f"Expected JSON object response, got {type(payload).__name__}."
            )
        return payload

    def extract_token(self, payload: dict[str, Any]) -> str:
        token = (
            payload.get("access_token")
            or payload.get("token")
            or payload.get("session_token")
        )
        if not isinstance(token, str) or not token.strip():
            self.logger.error("Authentication response token missing. Payload: %s", payload)
            raise AssertionError("Authentication response did not include a valid token.")
        return token

    def extract_ticket_id(self, payload: dict[str, Any]) -> str:
        ticket_id = payload.get("id") or payload.get("ticket_id")
        if ticket_id is None and isinstance(payload.get("data"), dict):
            ticket_id = payload["data"].get("id")

        if ticket_id is None:
            self.logger.error("Ticket id not found in payload: %s", payload)
            raise AssertionError("Ticket response did not include ticket id.")

        return str(ticket_id)
