import os
import csv
from datetime import datetime
from typing import List, Optional


# Handles real-time CSV data stream logging with immediate flush to disk
class CSVLogger:
    def __init__(self, filepath: Optional[str] = None, output_dir: str = "data/raw/run1", prefix: str = "log"):
        if filepath:
            self.filepath = filepath
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        else:
            self.output_dir = output_dir
            os.makedirs(self.output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.filepath = os.path.join(self.output_dir, f"{prefix}_{timestamp}.csv")

        self.file: Optional[csv.writer] = None
        self._raw_file = None

    # Opens log file stream and writes header fields
    def start(self, headers: List[str]) -> None:
        try:
            self._raw_file = open(self.filepath, mode="w", newline="", encoding="utf-8")
            self.file = csv.writer(self._raw_file)
            self.file.writerow(headers)
            print(f"[Logger] Started logging session: {self.filepath}")
        except Exception as err:
            print(f"[Logger] Error opening file: {err}")

    # Appends single row entry to CSV log stream
    def log_row(self, data: List) -> None:
        if self.file and self._raw_file:
            try:
                self.file.writerow(data)
                self._raw_file.flush()
            except Exception as err:
                print(f"[Logger] Row write failed: {err}")

    # Flushes and closes file handle safely
    def close(self) -> None:
        if self._raw_file:
            try:
                self._raw_file.close()
                print(f"[Logger] Log file saved cleanly: {self.filepath}")
            except Exception as err:
                print(f"[Logger] Error closing file: {err}")
            finally:
                self._raw_file = None
                self.file = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
