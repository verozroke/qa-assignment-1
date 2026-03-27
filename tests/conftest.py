from __future__ import annotations

import logging
import os

import requests

import pytest
from requests.exceptions import RequestException

from config.settings import Settings, get_settings
from utils.api_client import APIClient
from utils.logger import get_logger


def _is_truthy(value: str | None, default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _probe_http_target(url: str, timeout_seconds: int) -> tuple[bool, str]:
    try:
        response = requests.get(
            url,
            timeout=max(1, timeout_seconds),
            allow_redirects=True,
        )
        return True, f"HTTP {response.status_code}"
    except RequestException as exc:
        return False, str(exc)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if not items or not _is_truthy(os.getenv("SKIP_ON_UNREACHABLE"), default=True):
        return

    settings = get_settings()
    probe_timeout = min(settings.request_timeout, 5)
    logger = get_logger("qa-automation")

    api_url = f"{settings.api_base_url}{settings.api_auth_endpoint}"
    ui_url = f"{settings.ui_base_url}{settings.login_path}"

    api_ok, api_details = _probe_http_target(api_url, probe_timeout)
    ui_ok, ui_details = _probe_http_target(ui_url, probe_timeout)

    if not api_ok:
        logger.warning("API preflight probe failed for %s: %s", api_url, api_details)
    if not ui_ok:
        logger.warning("UI preflight probe failed for %s: %s", ui_url, ui_details)

    api_skip_reason = (
        f"API target unavailable at {api_url}. Details: {api_details}. "
        "Start the app or update API_BASE_URL/APP_BASE_URL in .env. "
        "Set SKIP_ON_UNREACHABLE=false to disable auto-skip behavior."
    )
    ui_skip_reason = (
        f"UI target unavailable at {ui_url}. Details: {ui_details}. "
        "Start the app or update UI_BASE_URL/APP_BASE_URL in .env. "
        "Set SKIP_ON_UNREACHABLE=false to disable auto-skip behavior."
    )

    for item in items:
        if "api" in item.keywords and not api_ok:
            item.add_marker(pytest.mark.skip(reason=api_skip_reason))
        if "ui" in item.keywords and not ui_ok:
            item.add_marker(pytest.mark.skip(reason=ui_skip_reason))


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


@pytest.fixture(scope="session")
def test_logger() -> logging.Logger:
    return get_logger("qa-automation")


@pytest.fixture(scope="session")
def api_client(settings: Settings, test_logger: logging.Logger):
    client = APIClient(settings=settings, logger=test_logger)
    yield client
    client.close()
