"""Fixtures for functional tests against a live Moonraker server."""

from __future__ import annotations

import os
from collections.abc import Generator

import pytest

from moonraker_client import MoonrakerClient


MOONRAKER_URL = os.environ.get("MOONRAKER_URL", "")
MOONRAKER_API_KEY = os.environ.get("MOONRAKER_API_KEY")


@pytest.fixture
def moonraker_url() -> str:
    """The Moonraker server URL for functional tests."""
    return MOONRAKER_URL


@pytest.fixture
def client() -> Generator[MoonrakerClient, None, None]:
    """A MoonrakerClient connected to the test server."""
    with MoonrakerClient(
        MOONRAKER_URL,
        api_key=MOONRAKER_API_KEY,
        timeout=10.0,
    ) as c:
        yield c
