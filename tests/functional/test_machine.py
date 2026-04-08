"""Functional tests for machine endpoints against a live Moonraker server."""

from __future__ import annotations

import pytest

from moonraker_client import MoonrakerClient

pytestmark = pytest.mark.functional


class TestMachineSystemInfo:
    def test_returns_system_info(self, client: MoonrakerClient) -> None:
        info = client.machine_systeminfo()
        assert "system_info" in info

    def test_system_info_has_cpu(self, client: MoonrakerClient) -> None:
        info = client.machine_systeminfo()
        sys_info = info["system_info"]
        assert "cpu_info" in sys_info


class TestMachineProcStats:
    def test_returns_stats(self, client: MoonrakerClient) -> None:
        stats = client.machine_procstats()
        assert "moonraker_stats" in stats
        assert "cpu_temp" in stats or "system_uptime" in stats
