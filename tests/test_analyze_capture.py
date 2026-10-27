import csv
import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.analyze_capture import REQUIRED, load_rows, summarize


class CaptureAnalysisTests(unittest.TestCase):
    def write_capture(self, rows):
        tmp = tempfile.NamedTemporaryFile(mode="w", newline="", suffix=".csv", delete=False)
        writer = csv.DictWriter(tmp, fieldnames=REQUIRED)
        writer.writeheader()
        writer.writerows(rows)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink, missing_ok=True)
        return Path(tmp.name)

    def row(self, t, current):
        values = {key: 0 for key in REQUIRED}
        values.update(time_ms=t, current_a=current, az_g=1, adc_raw=2000)
        return values

    def test_summary_metrics(self):
        path = self.write_capture([self.row(0, 1), self.row(20, 3), self.row(40, 2)])
        result = summarize(load_rows(path))
        self.assertEqual(result["sample_count"], 3)
        self.assertAlmostEqual(result["duration_s"], 0.04)
        self.assertAlmostEqual(result["current_a_mean"], 2.0)

    def test_rejects_non_increasing_time(self):
        path = self.write_capture([self.row(10, 1), self.row(10, 2)])
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            load_rows(path)

    def test_requires_two_samples(self):
        path = self.write_capture([self.row(0, 1)])
        with self.assertRaisesRegex(ValueError, "two numeric samples"):
            load_rows(path)


if __name__ == "__main__":
    unittest.main()
