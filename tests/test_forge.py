import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "config/includes.chroot/usr/local/bin/forge"
FORGE = ROOT / "forge/forge.py"
spec = importlib.util.spec_from_file_location("forge_module", FORGE)
forge_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forge_module)


class ForgeCliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args], text=True, capture_output=True, timeout=5)

    def test_version(self):
        p = self.run_cli("--version")
        self.assertEqual(p.returncode, 0)
        self.assertIn("forge 0.1.0-dev", p.stdout)

    def test_system_info_is_json(self):
        p = self.run_cli("system", "info")
        self.assertEqual(p.returncode, 0, p.stderr)
        data = json.loads(p.stdout)
        self.assertEqual(data["os"], "NebulaForge OS")
        self.assertIn("kernel", data)

    def test_game_list_handles_missing_library(self):
        p = self.run_cli("game", "list")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue("No imported games" in p.stdout or p.stdout.strip())

    def test_invalid_log_line_count_rejected(self):
        p = self.run_cli("logs", "--lines", "0")
        self.assertEqual(p.returncode, 2)
        self.assertIn("between 1 and 1000", p.stderr)

    def test_mutating_features_are_honestly_unimplemented(self):
        p = self.run_cli("package", "install")
        self.assertEqual(p.returncode, 3)
        self.assertIn("not implemented", p.stderr)

    def test_health_fails_when_required_systemd_check_fails(self):
        def fake_run(command):
            return (1, "failed") if command[:2] == ["systemctl", "is-system-running"] else (0, "ok")
        output = io.StringIO()
        with patch.object(forge_module, "run_readonly", side_effect=fake_run), contextlib.redirect_stdout(output):
            result = forge_module.system_health(None)
        self.assertEqual(result, 1)
        self.assertFalse(next(item for item in json.loads(output.getvalue()) if item["check"] == "systemd")["ok"])

    def test_health_does_not_fail_for_optional_network_or_vulkan(self):
        def fake_run(command):
            if command[:2] == ["systemctl", "is-active"]:
                return 1, "inactive"
            if command[:2] == ["sh", "-c"]:
                return 1, "missing"
            return 0, "ok"
        output = io.StringIO()
        with patch.object(forge_module, "run_readonly", side_effect=fake_run), contextlib.redirect_stdout(output):
            result = forge_module.system_health(None)
        self.assertEqual(result, 0)
        checks = json.loads(output.getvalue())
        self.assertFalse(next(item for item in checks if item["check"] == "network-manager")["ok"])
        self.assertFalse(next(item for item in checks if item["check"] == "vulkan")["ok"])


if __name__ == "__main__":
    unittest.main()
