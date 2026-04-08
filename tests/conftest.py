"""Shared test fixtures for the Moonraker client test suite."""

from __future__ import annotations

import os

import pytest


MOONRAKER_URL = os.environ.get("MOONRAKER_URL", "")


def pytest_configure(config: pytest.Config) -> None:
    """Register custom markers."""
    config.addinivalue_line("markers", "functional: tests requiring a live Moonraker server")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
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
