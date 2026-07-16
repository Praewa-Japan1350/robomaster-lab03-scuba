# src/gimbal.py
# คลาสควบคุมป้อมปืน/มุมกล้องก้มเงย


class GimbalController:
    """
    คลาสสำหรับควบคุม Gimbal (ป้อมปืน/กล้อง) ของ RoboMaster EP
    รองรับการหมุนซ้าย-ขวา (Yaw) และก้ม-เงย (Pitch)
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
        self.gimbal = ep_robot.gimbal
        gimbal_cfg = config["robot_params"]["gimbal"]
        self.pitch_speed = gimbal_cfg["default_pitch_speed"]
        self.yaw_speed = gimbal_cfg["default_yaw_speed"]
        self.max_pitch = gimbal_cfg["max_pitch_angle"]
        self.min_pitch = gimbal_cfg["min_pitch_angle"]
        print(f"[Gimbal] Initialized | pitch_speed={self.pitch_speed}, yaw_speed={self.yaw_speed}")

    def look_up(self, angle=10):
        """เงยกล้องขึ้น (องศา)"""
        angle = min(angle, self.max_pitch)
        print(f"[Gimbal] Looking up {angle}°")
        self.gimbal.move(pitch=angle, yaw=0, pitch_speed=self.pitch_speed,
                         yaw_speed=self.yaw_speed).wait_for_completed()

    def look_down(self, angle=10):
        """ก้มกล้องลง (องศา)"""
        angle = max(-angle, self.min_pitch)
        print(f"[Gimbal] Looking down {angle}°")
        self.gimbal.move(pitch=angle, yaw=0, pitch_speed=self.pitch_speed,
                         yaw_speed=self.yaw_speed).wait_for_completed()

    def turn_left(self, angle=30):
        """หมุน Gimbal ไปทางซ้าย (องศา)"""
        print(f"[Gimbal] Turning left {angle}°")
        self.gimbal.move(pitch=0, yaw=-angle, pitch_speed=self.pitch_speed,
                         yaw_speed=self.yaw_speed).wait_for_completed()

    def turn_right(self, angle=30):
        """หมุน Gimbal ไปทางขวา (องศา)"""
        print(f"[Gimbal] Turning right {angle}°")
        self.gimbal.move(pitch=0, yaw=angle, pitch_speed=self.pitch_speed,
                         yaw_speed=self.yaw_speed).wait_for_completed()

    def recenter(self):
        """คืนตำแหน่ง Gimbal กลับศูนย์กลาง"""
        print("[Gimbal] Recentering...")
        self.gimbal.recenter().wait_for_completed()
