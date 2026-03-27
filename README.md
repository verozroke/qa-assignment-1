# QA Assignment 1 — Risk Assessment & Environment Setup

Quality Assurance environment and risk-based test strategy for a web-based ticket management system.

## System Under Test

A web-based ticket management application with three layers:

- **Frontend** — login, dashboard, ticket creation, logout
- **Backend** — REST API with Bearer token authentication (`/api/auth/login`, `/api/tickets`, `/api/tickets/{id}`)
- **Database** — persists users and tickets

## Risk Assessment Summary

| Module          | Probability | Impact | Risk Level |
| --------------- | ----------- | ------ | ---------- |
| Authentication  | High        | High   | Critical   |
| Ticket Creation | High        | High   | Critical   |
| API Endpoints   | Medium      | High   | High       |
| Notifications   | Medium      | Medium | Medium     |
| Dashboard UI    | Low         | Low    | Low        |

Critical and High modules are automated first. See the full risk assessment in the deliverables document.

## Repository Structure

```
├── .github/workflows/qa-automation.yml   # CI/CD pipeline
├── config/
│   └── settings.py              # Environment-driven configuration
├── tests/
│   ├── conftest.py              # Shared fixtures, preflight probe
│   ├── api/
│   │   └── test_api_endpoints.py
│   └── ui/
│       ├── conftest.py          # Playwright fixtures
│       ├── test_login.py
│       ├── test_logout.py
│       └── test_create_ticket_flow.py
├── utils/
│   ├── api_client.py            # HTTP client wrapper
│   ├── base_test.py             # Shared test utilities
│   ├── logger.py                # Logging setup
│   └── ui_pages.py              # Page Object Model
├── .env.example
├── pytest.ini
└── requirements.txt
```

## Tools

| Tool           | Purpose                                                           |
| -------------- | ----------------------------------------------------------------- |
| Pytest         | Test framework with markers (`api`, `ui`) and JUnit XML reporting |
| Playwright     | UI automation (headless Chromium)                                 |
| Requests       | API testing via custom APIClient                                  |
| GitHub Actions | CI/CD pipeline                                                    |
| python-dotenv  | Environment-based configuration                                   |

## Setup

### Prerequisites

- Python 3.12+
- Node.js (for Playwright browser install)

### Installation

```bash
git clone https://github.com/almiinho/QA-Assignment-1.git
cd QA-Assignment-1
pip install -r requirements.txt
playwright install --with-deps chromium
```

### Configuration

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Key variables:

| Variable              | Description               | Default                 |
| --------------------- | ------------------------- | ----------------------- |
| `APP_BASE_URL`        | Application base URL      | `http://localhost:8080` |
| `TEST_USERNAME`       | Test user login           | `test.user`             |
| `TEST_PASSWORD`       | Test user password        | `ChangeMe123!`          |
| `UI_HEADLESS`         | Run browser headless      | `true`                  |
| `SKIP_ON_UNREACHABLE` | Skip tests if app is down | `true`                  |

### Running Tests

```bash
# Run all tests
pytest

# Run only API tests
pytest -m api

# Run only UI tests
pytest -m ui

# Generate JUnit XML report
pytest --junitxml=test-results/pytest-report.xml
```

## CI/CD Pipeline

GitHub Actions workflow runs on every push and PR to main:

1. Checkout repository
2. Setup Python 3.12
3. Install dependencies
4. Install Playwright browser
5. Run pytest with JUnit XML output
6. Upload test artifacts

The pipeline uses `SKIP_ON_UNREACHABLE=true` — if the target application is not reachable, tests are skipped gracefully instead of failing.

## Test Suite

| #   | Test                            | Type     | Priority |
| --- | ------------------------------- | -------- | -------- |
| 1   | Login with valid credentials    | UI + API | Critical |
| 2   | Login with invalid credentials  | UI       | Critical |
| 3   | Create ticket via API           | API      | Critical |
| 4   | Retrieve ticket by ID           | API      | High     |
| 5   | Create ticket with invalid data | API      | High     |
| 6   | Create ticket via UI            | UI       | Critical |
| 7   | Logout from dashboard           | UI       | High     |
| 8   | Authentication endpoint         | API      | Critical |

## Baseline Metrics

| Metric                              | Value            |
| ----------------------------------- | ---------------- |
| Total modules identified            | 5                |
| High-risk modules (Critical + High) | 3 of 5 (60%)     |
| Automated test cases                | 8 (4 API + 4 UI) |
| Critical module coverage            | 100%             |

## Course

Advanced Quality Assurance — Assignment 1 (Week 2)
