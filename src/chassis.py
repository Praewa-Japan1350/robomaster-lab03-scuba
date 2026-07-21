from typing import Optional, Dict, Any


class ChassisController:

    def __init__(self, ep_robot, config: Optional[Dict[str, Any]] = None):
        """
        ChassisController wrapper for RoboMaster EP chassis.

        Parameters
        ----------
        ep_robot : robot.Robot
            The RoboMaster EP robot instance.
        config : dict, optional
            Chassis parameters dictionary (from settings.yaml).
        """
        self.chassis = ep_robot.chassis
        self.ep_robot = ep_robot

        # Load parameters with defaults
        cfg = config or {}
        self.distance_trim = float(cfg.get("distance_trim", 1.0))
        self.turn_trim = float(cfg.get("turn_trim", 1.0))
        self.default_speed = float(cfg.get("default_speed_x", 0.5))
        self.enable_heading_correction = bool(cfg.get("enable_heading_correction", True))
        self.yaw_kp = float(cfg.get("yaw_kp", 0.05))

    # Move the robot forward by a specified distance in meters.
    def move_forward(self, speed: float, distance: float, wait: bool = True):
        calibrated_dist = distance * self.distance_trim
        print(f"[Chassis] Moving forward: {distance:.2f}m (calibrated: {calibrated_dist:.2f}m) at {speed} m/s")
        # Positive x moves forward along the longitudinal axis
        action = self.chassis.move(x=calibrated_dist, y=0, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()  # Block execution until movement finishes
        return action

    # Move the robot backward by a specified distance in meters.
    def move_backward(self, speed: float, distance: float, wait: bool = True):
        calibrated_dist = distance * self.distance_trim
        print(f"[Chassis] Moving backward: {distance:.2f}m (calibrated: {calibrated_dist:.2f}m) at {speed} m/s")
        # Negative x moves backward along the longitudinal axis
        action = self.chassis.move(x=-calibrated_dist, y=0, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Slide (strafe) the robot to the left by a specified distance in meters.
    def slide_left(self, speed: float, distance: float, wait: bool = True):
        calibrated_dist = distance * self.distance_trim
        print(f"[Chassis] Sliding left: {distance:.2f}m (calibrated: {calibrated_dist:.2f}m) at {speed} m/s")
        # Negative y strafes left along the lateral axis
        action = self.chassis.move(x=0, y=-calibrated_dist, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Slide (strafe) the robot to the right by a specified distance in meters.
    def slide_right(self, speed: float, distance: float, wait: bool = True):
        calibrated_dist = distance * self.distance_trim
        print(f"[Chassis] Sliding right: {distance:.2f}m (calibrated: {calibrated_dist:.2f}m) at {speed} m/s")
        # Positive y strafes right along the lateral axis
        action = self.chassis.move(x=0, y=calibrated_dist, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Turn the robot clockwise (right) by specified degrees.
    def turn_right(self, speed: float, degrees: float = 90, wait: bool = True):
        calibrated_deg = degrees * self.turn_trim
        print(f"[Chassis] Turning right: {degrees:.1f}° (calibrated: {calibrated_deg:.1f}°) at {speed} deg/s")
        # Negative z rotates clockwise
        action = self.chassis.move(x=0, y=0, z=-calibrated_deg, z_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Turn the robot counter-clockwise (left) by specified degrees.
    def turn_left(self, speed: float, degrees: float = 90, wait: bool = True):
        calibrated_deg = degrees * self.turn_trim
        print(f"[Chassis] Turning left: {degrees:.1f}° (calibrated: {calibrated_deg:.1f}°) at {speed} deg/s")
        # Positive z rotates counter-clockwise
        action = self.chassis.move(x=0, y=0, z=calibrated_deg, z_speed=speed)
        if wait:
            action.wait_for_completed()
        return action



