"""Shared test fixtures for the Moonraker client test suite."""

from __future__ import annotations

import importlib.util
import os

import pytest

MOONRAKER_URL = os.environ.get("MOONRAKER_URL", "")

# pytest-httpx dropped Python 3.8 support before it gained httpx>=0.27
# compatibility, so on 3.8 the mock-based unit tests that import
# ``pytest_httpx`` can't run. Skip collecting those files instead of
# failing with ImportError at collection time.
if importlib.util.find_spec("pytest_httpx") is None:
    collect_ignore_glob = [
        "unit/test_auth.py",
        "unit/test_client.py",
        "unit/api/test_auth_api.py",
        "unit/api/test_files.py",
        "unit/api/test_history.py",
        "unit/api/test_jobs.py",
        "unit/api/test_machine.py",
        "unit/api/test_printer.py",
        "unit/api/test_server.py",
    ]


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "functional: tests requiring a live Moonraker server")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-skip functional tests unless MOONRAKER_URL is set or --functional is passed."""
    run_functional = config.getoption("--functional", default=False)
    if run_functional and MOONRAKER_URL:
        return

    if run_functional and not MOONRAKER_URL:
        reason = "MOONRAKER_URL environment variable is required for functional tests"
    else:
        reason = "Functional tests require --functional flag and MOONRAKER_URL env var"

    skip_functional = pytest.mark.skip(reason=reason)
    for item in items:
        if "functional" in item.keywords:
            item.add_marker(skip_functional)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add --functional CLI option."""
    parser.addoption(
        "--functional",
        action="store_true",
        default=False,
        help="Run functional tests against a live Moonraker server",
    )
