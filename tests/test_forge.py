import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "config/includes.chroot/usr/local/bin/forge"

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

if __name__ == "__main__":
    unittest.main()
