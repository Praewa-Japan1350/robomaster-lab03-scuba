import csv
import os
import tempfile
import unittest

from src.logger import CSVLogger


class CSVLoggerTests(unittest.TestCase):
    def test_accepts_filepath_and_writes_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "sample.csv")
            logger = CSVLogger(filepath=filepath)
            logger.start(["a", "b"])
            logger.log_row([1, 2])
            logger.close()

            self.assertTrue(os.path.exists(filepath))
            with open(filepath, newline="", encoding="utf-8") as handle:
                rows = list(csv.reader(handle))

            self.assertEqual(rows[0], ["a", "b"])
            self.assertEqual(rows[1], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
