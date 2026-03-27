from __future__ import annotations

import logging
import re

from playwright.sync_api import Error as PlaywrightError, Page, expect

from config.settings import Settings


class LoginPage:
    def __init__(self, page: Page, settings: Settings, logger: logging.Logger) -> None:
        self.page = page
        self.settings = settings
        self.logger = logger

    def open(self) -> None:
        url = f"{self.settings.ui_base_url}{self.settings.login_path}"
        self.logger.info("Opening login page: %s", url)
        try:
            self.page.goto(url, wait_until="domcontentloaded")
        except PlaywrightError as exc:
            self.logger.exception("Unable to open login page.")
            raise RuntimeError("Unable to open login page.") from exc

    def login(self, username: str, password: str) -> None:
        self.logger.info("Submitting login form for user: %s", username)
        try:
            self.page.fill(self.settings.username_selector, username)
            self.page.fill(self.settings.password_selector, password)
            self.page.click(self.settings.login_button_selector)
        except PlaywrightError as exc:
            self.logger.exception("Unable to submit login form.")
            raise RuntimeError("Unable to submit login form.") from exc

    def assert_login_error_visible(self) -> None:
        self.logger.info("Checking invalid credential error visibility.")
        expect(self.page.locator(self.settings.login_error_selector)).to_be_visible(
            timeout=self.settings.ui_expect_timeout
        )

    def assert_login_form_visible(self) -> None:
        self.logger.info("Checking login form visibility.")
        expect(self.page.locator(self.settings.username_selector)).to_be_visible(
            timeout=self.settings.ui_expect_timeout
        )
        expect(self.page.locator(self.settings.password_selector)).to_be_visible(
            timeout=self.settings.ui_expect_timeout
        )


class DashboardPage:
    def __init__(self, page: Page, settings: Settings, logger: logging.Logger) -> None:
        self.page = page
        self.settings = settings
        self.logger = logger

    def assert_loaded(self) -> None:
        self.logger.info("Validating dashboard page is loaded.")
        expect(self.page).to_have_url(
            re.compile(f".*{re.escape(self.settings.dashboard_path)}"),
            timeout=self.settings.ui_expect_timeout,
        )
        expect(self.page.locator(self.settings.dashboard_marker_selector)).to_be_visible(
            timeout=self.settings.ui_expect_timeout
        )

    def open_create_ticket_form(self) -> None:
        url = f"{self.settings.ui_base_url}{self.settings.create_ticket_path}"
        self.logger.info("Opening create ticket form: %s", url)
        try:
            self.page.goto(url, wait_until="domcontentloaded")
        except PlaywrightError as exc:
            self.logger.exception("Unable to open create ticket form.")
            raise RuntimeError("Unable to open create ticket form.") from exc

    def create_ticket(self, title: str, description: str) -> None:
        self.logger.info("Creating ticket with title: %s", title)
        try:
            self.page.fill(self.settings.ticket_title_selector, title)
            self.page.fill(self.settings.ticket_description_selector, description)
            self.page.click(self.settings.ticket_submit_selector)
        except PlaywrightError as exc:
            self.logger.exception("Unable to submit create ticket form.")
            raise RuntimeError("Unable to submit create ticket form.") from exc

    def assert_ticket_created(self) -> None:
        self.logger.info("Checking ticket creation success message.")
        expect(self.page.locator(self.settings.ticket_success_selector)).to_be_visible(
            timeout=self.settings.ui_expect_timeout
        )

    def logout(self) -> None:
        self.logger.info("Logging out current user.")
        try:
            logout_button = self.page.locator(self.settings.logout_button_selector).first
            if logout_button.is_visible():
                logout_button.click()
                return

            self.page.click(self.settings.logout_menu_selector)
            self.page.click(self.settings.logout_button_selector)
        except PlaywrightError as exc:
            self.logger.exception("Unable to log out user.")
            raise RuntimeError("Unable to log out user.") from exc
