import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class InputStatusTests(unittest.TestCase):
    def run_updaters(self, payload, expected, selection="fixture"):
        for provider in ("github", "npm", "gitlab"):
            with self.subTest(provider=provider, payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "fixture.json"
                    original = json.dumps(payload).encode("utf-8")
                    path.write_bytes(original)
                    script = Path(__file__).with_name(f"update_sdks_metadata_{provider}.py")
                    result = subprocess.run(
                        [sys.executable, str(script), "--jsonfile", selection,
                         "--json-dir", directory], capture_output=True, text=True,
                    )
                    self.assertEqual(result.returncode, expected, result.stderr)
                    if expected:
                        self.assertIn("ERROR:", result.stderr)
                        self.assertNotIn("Traceback", result.stderr)
                        self.assertEqual(path.read_bytes(), original)
                    else:
                        self.assertEqual(json.loads(path.read_text()), payload)

    def test_missing_sdk_list(self):
        self.run_updaters({}, 2)

    def test_non_list_sdk_values(self):
        for value in (None, {}, "invalid", 1):
            self.run_updaters({"sdks": value}, 2)

    def test_non_object_root(self):
        for value in (None, [], "invalid", 1):
            self.run_updaters(value, 2)

    def test_invalid_batch_is_not_successful(self):
        self.run_updaters({}, 2, selection="all")

    def test_empty_sdk_list_is_valid(self):
        self.run_updaters({"sdks": []}, 0)


if __name__ == "__main__":
    unittest.main()
