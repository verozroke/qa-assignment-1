from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from utils.api_client import APIClient
from utils.base_test import BaseTest


@pytest.mark.api
class TestTicketAPI(BaseTest):
    def _get_auth_token(self, api_client: APIClient) -> str:
        response = api_client.authenticate(
            username=self.settings.username,
            password=self.settings.password,
        )
        self.assert_status_code(response, (200, 201), "Authentication precondition")
        payload = self.parse_json(response)
        return self.extract_token(payload)

    def _ticket_payload(self) -> dict[str, Any]:
        unique_suffix = datetime.now(tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        return {
            "title": f"API Automation Ticket {unique_suffix}",
            "description": "Ticket created by automated API validation.",
            "priority": "medium",
            "category": "general",
        }

    def test_authentication_endpoint(self, api_client: APIClient) -> None:
        self.log_step("Call authentication endpoint with valid credentials.")
        response = api_client.authenticate(
            username=self.settings.username,
            password=self.settings.password,
        )
        self.assert_status_code(response, (200, 201), "Authentication endpoint")

        payload = self.parse_json(response)
        token = self.extract_token(payload)
        assert token, "Expected a non-empty token from authentication endpoint."

    def test_create_ticket_endpoint(self, api_client: APIClient) -> None:
        token = self._get_auth_token(api_client)

        self.log_step("Create a ticket through API.")
        response = api_client.create_ticket(token=token, payload=self._ticket_payload())
        self.assert_status_code(response, (200, 201), "Create ticket endpoint")

        payload = self.parse_json(response)
        ticket_id = self.extract_ticket_id(payload)
        assert ticket_id, "Expected a ticket id in create ticket response."

    def test_get_ticket_endpoint(self, api_client: APIClient) -> None:
        token = self._get_auth_token(api_client)

        self.log_step("Create a ticket as precondition for retrieval.")
        create_response = api_client.create_ticket(token=token, payload=self._ticket_payload())
        self.assert_status_code(create_response, (200, 201), "Create ticket precondition")
        create_payload = self.parse_json(create_response)
        ticket_id = self.extract_ticket_id(create_payload)

        self.log_step("Get ticket by id through API.")
        get_response = api_client.get_ticket(token=token, ticket_id=ticket_id)
        self.assert_status_code(get_response, (200,), "Get ticket endpoint")
        ticket_payload = self.parse_json(get_response)

        resolved_id = (
            ticket_payload.get("id")
            or ticket_payload.get("ticket_id")
            or (ticket_payload.get("data") or {}).get("id")
        )
        assert str(resolved_id) == str(ticket_id), (
            f"Expected ticket id {ticket_id}, but got {resolved_id}."
        )

    def test_create_ticket_with_invalid_data(self, api_client: APIClient) -> None:
        token = self._get_auth_token(api_client)
        invalid_payload = {
            "title": "",
            "description": "",
            "priority": "not-valid-priority",
            "category": "",
        }

        self.log_step("Submit invalid ticket data and verify validation failure.")
        response = api_client.create_ticket(token=token, payload=invalid_payload)

        assert response.status_code in (400, 422), (
            "Expected 400/422 response for invalid ticket payload, "
            f"got {response.status_code}."
        )

        payload = self.parse_json(response)
        assert any(key in payload for key in ("error", "errors", "message", "detail")), (
            "Expected validation error details in response body."
        )
