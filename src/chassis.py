class ChassisController:

    def __init__(self, ep_robot):
        # Bind the chassis module from the main robot instance
        self.chassis = ep_robot.chassis

    # Move the robot forward by a specified distance in meters.
    def move_forward(self, speed, distance, wait=True):
        print(f"[Chassis] Moving forward: {distance}m at {speed} m/s")
        # Positive x moves forward along the longitudinal axis
        action = self.chassis.move(x=distance, y=0, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()  # Block execution until movement finishes
        return action

    # Move the robot backward by a specified distance in meters.
    def move_backward(self, speed, distance, wait=True):
        print(f"[Chassis] Moving backward: {distance}m at {speed} m/s")
        # Negative x moves backward along the longitudinal axis
        action = self.chassis.move(x=-distance, y=0, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Slide (strafe) the robot to the left by a specified distance in meters.
    def slide_left(self, speed, distance, wait=True):
        print(f"[Chassis] Sliding left: {distance}m at {speed} m/s")
        # Negative y strafes left along the lateral axis
        action = self.chassis.move(x=0, y=-distance, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Slide (strafe) the robot to the right by a specified distance in meters.
    def slide_right(self, speed, distance, wait=True):
        print(f"[Chassis] Sliding right: {distance}m at {speed} m/s")
        # Positive y strafes right along the lateral axis
        action = self.chassis.move(x=0, y=distance, z=0, xy_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Turn the robot clockwise (right) by specified degrees.
    def turn_right(self, speed, degrees=90, wait=True):
        print(f"[Chassis] Turning right: {degrees} degrees at {speed} deg/s")
        # Negative z rotates clockwise
        action = self.chassis.move(x=0, y=0, z=-degrees, z_speed=speed)
        if wait:
            action.wait_for_completed()
        return action

    # Turn the robot counter-clockwise (left) by specified degrees.
    def turn_left(self, speed, degrees=90, wait=True):
        print(f"[Chassis] Turning left: {degrees} degrees at {speed} deg/s")
        # Positive z rotates counter-clockwise
        action = self.chassis.move(x=0, y=0, z=degrees, z_speed=speed)
        if wait:
            action.wait_for_completed()
        return action


