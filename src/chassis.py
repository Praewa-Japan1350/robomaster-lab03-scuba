# src/chassis.py
# คลาสควบคุมล้อ Mecanum (เดินหน้า, ถอยหลัง, สไลด์ข้าง)


class ChassisController:
    """
    คลาสสำหรับควบคุมล้อ Mecanum ของ RoboMaster EP
    รองรับการเคลื่อนที่: เดินหน้า, ถอยหลัง, สไลด์ซ้าย-ขวา, หมุนตัว
    """

    def __init__(self, ep_robot, config):
        """
        Parameters
        ----------
        ep_robot : robomaster.robot.Robot
            instance ของหุ่นยนต์ที่เชื่อมต่อแล้ว
        config : dict
            Dictionary ตั้งค่าจาก settings.yaml
        """
        self.chassis = ep_robot.chassis
        chassis_cfg = config["robot_params"]["chassis"]
        self.default_speed_x = chassis_cfg["default_speed_x"]
        self.default_speed_y = chassis_cfg["default_speed_y"]
        self.max_speed_x = chassis_cfg["max_speed_x"]
        print(f"[Chassis] Initialized | speed_x={self.default_speed_x}, speed_y={self.default_speed_y}")

    def move_forward(self, distance=0.5, speed=None):
        """เดินหน้าตามระยะที่กำหนด (เมตร)"""
        spd = speed if speed else self.default_speed_x
        spd = min(spd, self.max_speed_x)  # จำกัดความเร็วสูงสุด
        print(f"[Chassis] Moving forward {distance}m at {spd} m/s")
        self.chassis.move(x=distance, y=0, z=0, xy_speed=spd).wait_for_completed()

    def move_backward(self, distance=0.5, speed=None):
        """ถอยหลังตามระยะที่กำหนด (เมตร)"""
        spd = speed if speed else self.default_speed_x
        spd = min(spd, self.max_speed_x)
        print(f"[Chassis] Moving backward {distance}m at {spd} m/s")
        self.chassis.move(x=-distance, y=0, z=0, xy_speed=spd).wait_for_completed()

    def slide_left(self, distance=0.5, speed=None):
        """สไลด์ซ้ายตามระยะที่กำหนด (เมตร)"""
        spd = speed if speed else self.default_speed_y
        print(f"[Chassis] Sliding left {distance}m at {spd} m/s")
        self.chassis.move(x=0, y=-distance, z=0, xy_speed=spd).wait_for_completed()

    def slide_right(self, distance=0.5, speed=None):
        """สไลด์ขวาตามระยะที่กำหนด (เมตร)"""
        spd = speed if speed else self.default_speed_y
        print(f"[Chassis] Sliding right {distance}m at {spd} m/s")
        self.chassis.move(x=0, y=distance, z=0, xy_speed=spd).wait_for_completed()

    def rotate(self, angle=90, speed=50):
        """หมุนตัวตามองศาที่กำหนด (บวก=ทวนเข็ม, ลบ=ตามเข็ม)"""
        print(f"[Chassis] Rotating {angle}° at {speed} °/s")
        self.chassis.move(x=0, y=0, z=angle, z_speed=speed).wait_for_completed()

    def stop(self):
        """หยุดล้อทันที"""
        print("[Chassis] Stopping...")
        self.chassis.drive_speed(x=0, y=0, z=0)
