from __future__ import annotations

import re

import pytest
from playwright.sync_api import Page

from utils.base_test import BaseTest
from utils.ui_pages import DashboardPage, LoginPage


@pytest.mark.ui
class TestLogin(BaseTest):
    def test_login_with_valid_credentials(self, page: Page) -> None:
        login_page = LoginPage(page=page, settings=self.settings, logger=self.logger)
        dashboard_page = DashboardPage(page=page, settings=self.settings, logger=self.logger)

        self.log_step("Open login page.")
        login_page.open()

        self.log_step("Submit valid credentials.")
        login_page.login(self.settings.username, self.settings.password)

        self.log_step("Assert dashboard is loaded after successful login.")
        dashboard_page.assert_loaded()
        assert re.search(re.escape(self.settings.dashboard_path), page.url), (
            f"Expected URL to include {self.settings.dashboard_path}, got {page.url}."
        )

    def test_login_with_invalid_credentials(self, page: Page) -> None:
        login_page = LoginPage(page=page, settings=self.settings, logger=self.logger)

        self.log_step("Open login page.")
        login_page.open()

        self.log_step("Submit invalid credentials.")
        login_page.login(self.settings.username, self.settings.invalid_password)

        self.log_step("Assert invalid login feedback is displayed.")
        login_page.assert_login_error_visible()
        assert re.search(re.escape(self.settings.login_path), page.url), (
            f"Expected URL to include {self.settings.login_path}, got {page.url}."
        )
