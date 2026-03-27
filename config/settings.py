from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


load_dotenv()


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _to_int(value: str | None, default: int) -> int:
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"Expected an integer value, got '{value}'.") from exc


def _normalize_path(path_value: str) -> str:
    return path_value if path_value.startswith("/") else f"/{path_value}"


@dataclass(frozen=True)
class Settings:
    app_base_url: str
    api_base_url: str
    ui_base_url: str

    username: str
    password: str
    invalid_password: str

    request_timeout: int
    ui_headless: bool
    ui_slow_mo: int
    ui_expect_timeout: int

    api_auth_endpoint: str
    api_tickets_endpoint: str
    auth_header_prefix: str

    login_path: str
    dashboard_path: str
    create_ticket_path: str

    username_selector: str
    password_selector: str
    login_button_selector: str
    login_error_selector: str
    dashboard_marker_selector: str
    ticket_title_selector: str
    ticket_description_selector: str
    ticket_submit_selector: str
    ticket_success_selector: str
    logout_menu_selector: str
    logout_button_selector: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    app_base_url = os.getenv("APP_BASE_URL", "http://localhost:8080").rstrip("/")
    api_base_url = os.getenv("API_BASE_URL", app_base_url).rstrip("/")
    ui_base_url = os.getenv("UI_BASE_URL", app_base_url).rstrip("/")

    return Settings(
        app_base_url=app_base_url,
        api_base_url=api_base_url,
        ui_base_url=ui_base_url,
        username=os.getenv("TEST_USERNAME", "test.user"),
        password=os.getenv("TEST_PASSWORD", "ChangeMe123!"),
        invalid_password=os.getenv("INVALID_TEST_PASSWORD", "WrongPassword123!"),
        request_timeout=_to_int(os.getenv("REQUEST_TIMEOUT"), 30),
        ui_headless=_to_bool(os.getenv("UI_HEADLESS"), True),
        ui_slow_mo=_to_int(os.getenv("UI_SLOW_MO"), 0),
        ui_expect_timeout=_to_int(os.getenv("UI_EXPECT_TIMEOUT"), 10000),
        api_auth_endpoint=_normalize_path(
            os.getenv("API_AUTH_ENDPOINT", "/api/auth/login")
        ),
        api_tickets_endpoint=_normalize_path(
            os.getenv("API_TICKETS_ENDPOINT", "/api/tickets")
        ),
        auth_header_prefix=os.getenv("AUTH_HEADER_PREFIX", "Bearer").strip(),
        login_path=_normalize_path(os.getenv("LOGIN_PATH", "/login")),
        dashboard_path=_normalize_path(os.getenv("DASHBOARD_PATH", "/dashboard")),
        create_ticket_path=_normalize_path(
            os.getenv("CREATE_TICKET_PATH", "/tickets/new")
        ),
        username_selector=os.getenv("UI_USERNAME_SELECTOR", "input[name='username']"),
        password_selector=os.getenv("UI_PASSWORD_SELECTOR", "input[name='password']"),
        login_button_selector=os.getenv(
            "UI_LOGIN_BUTTON_SELECTOR", "button[type='submit']"
        ),
        login_error_selector=os.getenv("UI_LOGIN_ERROR_SELECTOR", ".alert-danger"),
        dashboard_marker_selector=os.getenv("UI_DASHBOARD_MARKER_SELECTOR", "main"),
        ticket_title_selector=os.getenv(
            "UI_TICKET_TITLE_SELECTOR", "input[name='title']"
        ),
        ticket_description_selector=os.getenv(
            "UI_TICKET_DESCRIPTION_SELECTOR", "textarea[name='description']"
        ),
        ticket_submit_selector=os.getenv(
            "UI_TICKET_SUBMIT_SELECTOR", "button[type='submit']"
        ),
        ticket_success_selector=os.getenv("UI_TICKET_SUCCESS_SELECTOR", ".alert-success"),
        logout_menu_selector=os.getenv(
            "UI_LOGOUT_MENU_SELECTOR", "[data-testid='user-menu']"
        ),
        logout_button_selector=os.getenv("UI_LOGOUT_BUTTON_SELECTOR", "text=Logout"),
    )
