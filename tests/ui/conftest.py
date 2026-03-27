from __future__ import annotations

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from config.settings import Settings


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, settings: Settings) -> Browser:
    browser = playwright_instance.chromium.launch(
        headless=settings.ui_headless,
        slow_mo=settings.ui_slow_mo,
    )
    yield browser
    browser.close()


@pytest.fixture
def context(browser: Browser) -> BrowserContext:
    context = browser.new_context(ignore_https_errors=True)
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext, settings: Settings) -> Page:
    page = context.new_page()
    page.set_default_timeout(settings.ui_expect_timeout)
    yield page
    page.close()
