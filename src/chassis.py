class ChassisController:
    """
    Class to control the Mecanum wheels chassis (forward, backward, sliding sideways, turning).
    Wraps the RoboMaster SDK chassis object with custom helper functions and sensor subscriptions.
    """
    def __init__(self, ep_robot):
        self.chassis = ep_robot.chassis

    def move_forward(self, speed, distance):
        """Moves the robot forward by a specified distance in meters."""
        print(f"[Chassis] Moving forward: {distance}m at {speed} m/s")
        return self.chassis.move(x=distance, y=0, z=0, xy_speed=speed)

    def move_backward(self, speed, distance):
        """Moves the robot backward by a specified distance in meters."""
        print(f"[Chassis] Moving backward: {distance}m at {speed} m/s")
        return self.chassis.move(x=-distance, y=0, z=0, xy_speed=speed)

    def slide_left(self, speed, distance):
        """Slides the robot to the left by a specified distance in meters."""
        print(f"[Chassis] Sliding left: {distance}m at {speed} m/s")
        return self.chassis.move(x=0, y=-distance, z=0, xy_speed=speed)

    def slide_right(self, speed, distance):
        """Slides the robot to the right by a specified distance in meters."""
        print(f"[Chassis] Sliding right: {distance}m at {speed} m/s")
        return self.chassis.move(x=0, y=distance, z=0, xy_speed=speed)

    def turn_right(self, speed_z, angle=90):
        """Rotates the robot to the right (clockwise) by a specified angle in degrees."""
        print(f"[Chassis] Turning right: {angle} deg at {speed_z} deg/s")
        return self.chassis.move(x=0, y=0, z=-angle, z_speed=speed_z)

    def turn_left(self, speed_z, angle=90):
        """Rotates the robot to the left (counter-clockwise) by a specified angle in degrees."""
        print(f"[Chassis] Turning left: {angle} deg at {speed_z} deg/s")
        return self.chassis.move(x=0, y=0, z=angle, z_speed=speed_z)

    def stop(self):
        """Actively locks/brakes chassis motors to prevent coasting and drifting."""
        self.chassis.drive_speed(x=0, y=0, z=0)

    def start_subscriptions(self, pos_cb=None, att_cb=None, imu_cb=None, freq=10):
        """Subscribes to chassis position, attitude, and IMU data."""
        if pos_cb:
            self.chassis.sub_position(freq=freq, callback=pos_cb)
        if att_cb:
            self.chassis.sub_attitude(freq=freq, callback=att_cb)
        if imu_cb:
            try:
                self.chassis.sub_imu(freq=freq, callback=imu_cb)
            except Exception as e:
                print(f"[Chassis] IMU subscription notice: {e}")

    def stop_subscriptions(self):
        """Unsubscribes from chassis position, attitude, and IMU data."""
        try:
            self.chassis.unsub_position()
        except Exception:
            pass
        try:
            self.chassis.unsub_attitude()
        except Exception:
            pass
        try:
            self.chassis.unsub_imu()
        except Exception:
            pass


current_pos = {"x": 0.0, "y": 0.0, "z": 0.0}
current_att = {"yaw": 0.0, "pitch": 0.0, "roll": 0.0}
current_imu = {"acc_x": 0.0, "acc_y": 0.0, "acc_z": 0.0, "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0}

def sub_position_handler(position_info):
    current_pos["x"], current_pos["y"], current_pos["z"] = position_info

def sub_attitude_handler(attitude_info):
    current_att["yaw"], current_att["pitch"], current_att["roll"] = attitude_info

def sub_imu_handler(imu_info):
    current_imu["acc_x"], current_imu["acc_y"], current_imu["acc_z"], \
    current_imu["gyro_x"], current_imu["gyro_y"], current_imu["gyro_z"] = imu_info

def get_current_pos():
    return current_pos

def get_current_att():
    return current_att

def get_current_imu():
    return current_imu