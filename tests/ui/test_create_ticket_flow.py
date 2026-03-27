from __future__ import annotations

from datetime import datetime, timezone

import pytest
from playwright.sync_api import Page

from utils.base_test import BaseTest
from utils.ui_pages import DashboardPage, LoginPage


@pytest.mark.ui
class TestCreateTicketFlow(BaseTest):
    def test_create_ticket_flow(self, page: Page) -> None:
        login_page = LoginPage(page=page, settings=self.settings, logger=self.logger)
        dashboard_page = DashboardPage(page=page, settings=self.settings, logger=self.logger)

        ticket_title = (
            f"Automation Ticket {datetime.now(tz=timezone.utc).strftime('%Y%m%d%H%M%S')}"
        )
        ticket_description = "Ticket created by Playwright UI automation suite."

        self.log_step("Authenticate through UI.")
        login_page.open()
        login_page.login(self.settings.username, self.settings.password)
        dashboard_page.assert_loaded()

        self.log_step("Open create ticket form and submit a new ticket.")
        dashboard_page.open_create_ticket_form()
        dashboard_page.create_ticket(ticket_title, ticket_description)

        self.log_step("Assert ticket creation confirmation is visible.")
        dashboard_page.assert_ticket_created()
        assert (
            self.settings.create_ticket_path in page.url
            or self.settings.dashboard_path in page.url
        ), f"Unexpected URL after ticket creation: {page.url}."
