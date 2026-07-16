# src/logger.py
# คลาสจัดการเขียนค่าจากเซนเซอร์ลงไฟล์ CSV แบบเรียลไทม์

import os
import csv
from datetime import datetime


class SensorLogger:
    """
    คลาสสำหรับบันทึกข้อมูลจากเซนเซอร์ (IMU, chassis status ฯลฯ) ลงไฟล์ CSV แบบเรียลไทม์
    สร้างโฟลเดอร์ run แยกตามจำนวนครั้งที่กดรันอัตโนมัติ
    """

    def __init__(self, config, sensor_name="imu"):
        """
        Parameters
        ----------
        config : dict
            Dictionary ตั้งค่าจาก settings.yaml
        sensor_name : str
            ชื่อเซนเซอร์สำหรับตั้งชื่อไฟล์ เช่น "imu", "chassis"
        """
        self.raw_dir = config["paths"]["raw_data_dir"]
        self.sensor_name = sensor_name
        self._file = None
        self._writer = None
        self._run_dir = None
        self._row_count = 0

    def _get_next_run_dir(self):
        """หาหมายเลข run ถัดไปที่ยังไม่มีโฟลเดอร์"""
        run_num = 1
        while True:
            run_dir = os.path.join(self.raw_dir, f"run{run_num}")
            if not os.path.exists(run_dir):
                return run_dir, run_num
            run_num += 1

    def start(self, headers=None):
        """
        เปิดไฟล์ CSV พร้อมเขียน header

        Parameters
        ----------
        headers : list of str, optional
            ชื่อคอลัมน์  (ค่าเริ่มต้น: ["timestamp", "acc_x", "acc_y", "acc_z",
            "gyro_x", "gyro_y", "gyro_z"])
        """
        if headers is None:
            headers = ["timestamp", "acc_x", "acc_y", "acc_z",
                       "gyro_x", "gyro_y", "gyro_z"]

        self._run_dir, run_num = self._get_next_run_dir()
        os.makedirs(self._run_dir, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"log_{date_str}_{self.sensor_name}.csv"
        filepath = os.path.join(self._run_dir, filename)

        self._file = open(filepath, "w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._file)
        self._writer.writerow(headers)
        self._row_count = 0

        print(f"[Logger] Started logging to: {filepath}  (run{run_num})")

    def log(self, row_data):
        """
        เขียนข้อมูล 1 แถวลงไฟล์ CSV

        Parameters
        ----------
        row_data : list
            ข้อมูล 1 แถว เช่น [timestamp, acc_x, acc_y, ...]
        """
        if self._writer is None:
            print("[Logger] WARNING: Logger not started. Call start() first.")
            return
        self._writer.writerow(row_data)
        self._row_count += 1
        # flush ทุก 10 แถว เพื่อป้องกันข้อมูลหายถ้าโปรแกรมพัง
        if self._row_count % 10 == 0:
            self._file.flush()

    def stop(self):
        """ปิดไฟล์ CSV"""
        if self._file is not None:
            self._file.flush()
            self._file.close()
            self._file = None
            self._writer = None
            print(f"[Logger] Stopped. Total rows logged: {self._row_count}")
