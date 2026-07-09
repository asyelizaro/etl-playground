import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from engine import run_table


class EngineDryRunTest(unittest.TestCase):
    def test_run_table_dry_run_returns_plan(self):
        result = run_table("artist", dt="2026-07-06", dry_run=True)

        self.assertEqual(result["table"], "artist")
        self.assertEqual(result["handler"], "artist_legacy.load_artist")
        self.assertEqual(result["target_table"], "artist_hub")
        self.assertEqual(result["database"], "silver")
        self.assertEqual(result["partition_dt"], "2026-07-06")
        self.assertEqual(result["mode"], "dry-run")


if __name__ == "__main__":
    unittest.main()
