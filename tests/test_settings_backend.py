import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("nebula_settings_backend", ROOT / "desktop/nebula_settings_backend.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class SettingsBackendTests(unittest.TestCase):
    def test_missing_tools_are_reported_as_unavailable(self):
        result = MODULE.system_summary(which=lambda _name: None, run=Mock())
        self.assertIn("Kernel: unavailable (missing uname)", result)
        self.assertIn("Network: unavailable (missing nmcli)", result)

    def test_nonzero_command_is_not_reported_as_success(self):
        run = Mock(return_value=subprocess.CompletedProcess([], 1, "secret failure detail\n"))
        result = MODULE.system_summary(which=lambda _name: True, run=run)
        self.assertIn("Kernel: unavailable", result)
        self.assertNotIn("secret failure detail", result)

    def test_command_output_is_bounded(self):
        run = Mock(return_value=subprocess.CompletedProcess([], 0, "x" * 500 + "\nsecond line"))
        result = MODULE.system_summary(which=lambda _name: True, run=run)
        self.assertIn("x" * 180, result)
        self.assertNotIn("second line", result)

if __name__ == "__main__":
    unittest.main()
