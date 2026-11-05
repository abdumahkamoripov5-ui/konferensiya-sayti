"""Configuration checks without loading real credentials or databases."""
import os
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch


class ConfigurationTests(unittest.TestCase):
    def load_config(self, environment, dotenv=""):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "config.py"
            target.write_bytes((Path(__file__).resolve().parents[1] / "config.py").read_bytes())
            (Path(directory) / ".env").write_text(dotenv, encoding="utf-8")
            with patch.dict(os.environ, environment, clear=True):
                return runpy.run_path(str(target))["Config"]

    def test_dotenv_loads_and_host_environment_takes_precedence(self):
        cfg = self.load_config(
            {"SECRET_KEY": "environment-secret-with-at-least-32-characters"},
            "SECRET_KEY=file-secret\nADMIN_LOGIN=local-admin\nMAX_UPLOAD_MB=3\n",
        )
        self.assertEqual(cfg.ADMIN_LOGIN, "local-admin")
        self.assertEqual(cfg.SECRET_KEY, "environment-secret-with-at-least-32-characters")
        self.assertEqual(cfg.MAX_UPLOAD_BYTES, 3 * 1024 * 1024)

    def test_vercel_caps_upload_and_total_request(self):
        for configured, expected in (("9", 4 * 1024 * 1024), ("2", 2 * 1024 * 1024)):
            with self.subTest(configured=configured):
                cfg = self.load_config({
                    "VERCEL": "1", "SECRET_KEY": "test-secret-with-at-least-32-characters",
                    "MAX_UPLOAD_MB": configured,
                })
                self.assertEqual(cfg.MAX_UPLOAD_BYTES, expected)
                self.assertEqual(cfg.MAX_UPLOAD_MB, expected / 1048576)
                self.assertLessEqual(cfg.MAX_CONTENT_LENGTH, 4_500_000)
                self.assertGreater(cfg.MAX_CONTENT_LENGTH, cfg.MAX_UPLOAD_BYTES)
