import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("cloudroomctl", Path(__file__).with_name("cloudroomctl.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class CloudroomBridgeTests(unittest.TestCase):
    def test_loopback_only(self):
        with patch.dict("os.environ", {"CLOUDROOM_API_URL": "http://127.0.0.1:9840"}):
            self.assertEqual(mod.endpoint_base(), "http://127.0.0.1:9840")
        for bad in ("https://example.com", "http://0.0.0.0:9840", "http://127.0.0.1:9840/unsafe"):
            with patch.dict("os.environ", {"CLOUDROOM_API_URL": bad}):
                with self.assertRaises(mod.CloudroomError):
                    mod.endpoint_base()

    def test_id_validation(self):
        self.assertEqual(mod.require_id("abc_01-hello"), "abc_01-hello")
        for bad in ("../secret", "", "name space", "slash/x", "a" * 101):
            with self.assertRaises(mod.CloudroomError):
                mod.require_id(bad)

    def test_token_without_file(self):
        with patch.dict("os.environ", {"CLOUDROOM_TOKEN_FILE": "/nonexistent/s2-cloudroom-token"}):
            self.assertIsNone(mod.token())

    def test_status_no_token_is_fail_closed(self):
        with patch.object(mod, "repo_status", return_value={"path": "/tmp", "git_exit_code": 0}):
            with patch.dict("os.environ", {"CLOUDROOM_TOKEN_FILE": "/nonexistent/s2-cloudroom-token"}):
                result = mod.run(type("Args", (), {"command": "status"})())
                self.assertFalse(result["core_ready"])
                self.assertIn("not configured", result["core_error"])


if __name__ == "__main__":
    unittest.main()
