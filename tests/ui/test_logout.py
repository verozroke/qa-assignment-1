from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page

from utils.base_test import BaseTest
from utils.ui_pages import DashboardPage, LoginPage


@pytest.mark.ui
class TestLogout(BaseTest):
    def test_logout(self, page: Page) -> None:
        login_page = LoginPage(page=page, settings=self.settings, logger=self.logger)
        dashboard_page = DashboardPage(page=page, settings=self.settings, logger=self.logger)

        self.log_step("Log in before logout validation.")
        login_page.open()
        login_page.login(self.settings.username, self.settings.password)
        dashboard_page.assert_loaded()

        self.log_step("Logout from the dashboard.")
        dashboard_page.logout()

        self.log_step("Assert login page is visible after logout.")
        login_page.assert_login_form_visible()
        assert re.search(re.escape(self.settings.login_path), page.url), (
            f"Expected URL to include {self.settings.login_path}, got {page.url}."
        )
