import sys
import os
import time
import threading
from typing import Dict, Any

# Ensure workspace root is in sys.path
workspace_root = os.path.dirname(os.path.abspath(__file__))
if workspace_root not in sys.path:
    sys.path.insert(0, workspace_root)

from robomaster import robot

from src.config_loader import load_settings
from src.logger import CSVLogger
from src.chassis import ChassisController

# Path navigation and sampling configuration
TILE_SIZE      = 0.5     # Tile length in meters
TILES_PER_SIDE = 2       # Grid dimension (2 tiles = 1.0 m)
MOVE_DIST      = TILE_SIZE

STOP_TIME      = 1.0     # Pause duration at each tile center (sec)
TURN_DEG       = -90     # Rotation angle (-90 = right turn)
TURN_SPEED     = 45      # Turn speed (deg/s)

SAMPLE_HZ      = 10      # Telemetry logging frequency (Hz)
SAMPLE_DT      = 1.0 / SAMPLE_HZ

CSV_HEADERS = [
    "step", "time_s", "phase",
    "acc_x", "acc_y", "acc_z",
    "gyro_x", "gyro_y", "gyro_z",
    "pos_x", "pos_y", "pos_z",
    "yaw", "pitch", "roll",
    "latency_ms",
]


# Thread-safe telemetry data collector and logger
class TelemetryRecorder:
    def __init__(self, ep_robot: robot.Robot, logger: CSVLogger):
        self.ep_robot = ep_robot
        self.logger = logger
        self._lock = threading.Lock()
        self._phase_lock = threading.Lock()
        
        self.current_phase = "idle"
        self.sensor_data: Dict[str, float] = {
            "acc_x": 0.0,  "acc_y": 0.0,  "acc_z": 0.0,
            "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0,
            "pos_x": 0.0,  "pos_y": 0.0,  "pos_z": 0.0,
            "yaw":   0.0,  "pitch": 0.0,  "roll":  0.0,
        }

    # Set active execution phase tag
    def set_phase(self, phase_name: str) -> None:
        with self._phase_lock:
            self.current_phase = phase_name
        print(f"\n[Phase] ▶ {phase_name}")

    # IMU telemetry callback
    def on_imu_update(self, imu_info: Any) -> None:
        with self._lock:
            self.sensor_data["acc_x"]  = imu_info[0]
            self.sensor_data["acc_y"]  = imu_info[1]
            self.sensor_data["acc_z"]  = imu_info[2]
            self.sensor_data["gyro_x"] = imu_info[3]
            self.sensor_data["gyro_y"] = imu_info[4]
            self.sensor_data["gyro_z"] = imu_info[5]

    # Position telemetry callback
    def on_position_update(self, pos_info: Any) -> None:
        with self._lock:
            self.sensor_data["pos_x"] = pos_info[0]
            self.sensor_data["pos_y"] = pos_info[1]
            self.sensor_data["pos_z"] = pos_info[2]

    # Attitude angle telemetry callback
    def on_attitude_update(self, att_info: Any) -> None:
        with self._lock:
            self.sensor_data["yaw"]   = att_info[0]
            self.sensor_data["pitch"] = att_info[1]
            self.sensor_data["roll"]  = att_info[2]

    # Recording thread execution loop
    def recording_worker(self, start_time: float, stop_event: threading.Event) -> None:
        step = 0
        while not stop_event.is_set():
            t_lat_start = time.time()
            try:
                self.ep_robot.get_version()
                latency_ms = (time.time() - t_lat_start) * 1000.0
            except Exception:
                latency_ms = -1.0

            elapsed = time.time() - start_time

            with self._phase_lock:
                phase = self.current_phase
            with self._lock:
                s = dict(self.sensor_data)

            row = [
                step,
                round(elapsed, 4),
                phase,
                round(s["acc_x"], 4), round(s["acc_y"], 4), round(s["acc_z"], 4),
                round(s["gyro_x"], 4), round(s["gyro_y"], 4), round(s["gyro_z"], 4),
                round(s["pos_x"], 4), round(s["pos_y"], 4), round(s["pos_z"], 4),
                round(s["yaw"], 4), round(s["pitch"], 4), round(s["roll"], 4),
                round(latency_ms, 2),
            ]

            self.logger.log_row(row)

            print(
                f"[{step:05d}] t={elapsed:7.3f}s | phase={phase:<26s} | "
                f"pos=({s['pos_x']:+.3f},{s['pos_y']:+.3f}) m | "
                f"yaw={s['yaw']:+.1f}° | latency={latency_ms:6.1f} ms"
            )

            step += 1
            time.sleep(SAMPLE_DT)


def main():
    config = load_settings()
    speed = config["robot_params"]["chassis"]["default_speed_x"]

    logger = CSVLogger(output_dir="data/raw/run1", prefix="square_path")
    logger.start(CSV_HEADERS)

    print("[Main] Connecting to RoboMaster EP...")
    ep_robot = robot.Robot()
    stop_event = threading.Event()
    rec_thread = None

    try:
        ep_robot.initialize(conn_type="ap")
        print("[Main] Connected! SN:", ep_robot.get_sn())
        chassis_ctrl = ChassisController(ep_robot, config=config["robot_params"]["chassis"])

        recorder = TelemetryRecorder(ep_robot, logger)

        chassis.sub_imu(freq=SAMPLE_HZ, callback=recorder.on_imu_update)
        chassis.sub_position(freq=SAMPLE_HZ, callback=recorder.on_position_update)
        chassis.sub_attitude(freq=SAMPLE_HZ, callback=recorder.on_attitude_update)
        time.sleep(0.5)

        start_time = time.time()
        recorder.set_phase("init")
        rec_thread = threading.Thread(
            target=recorder.recording_worker,
            args=(start_time, stop_event),
            daemon=True,
        )
        rec_thread.start()

        cardinal_sides = ["north", "east", "south", "west"]

        print("\n[Main] ════════════════════════════════════════")
        print("[Main] Starting 2x2 Square Path + Latency Measurement")
        print(f"[Main] Side distance = {TILES_PER_SIDE * TILE_SIZE:.2f} m")
        print(f"[Main] Speed = {speed} m/s | Turn Speed = {TURN_SPEED} deg/s")
        print(f"[Main] Calibration Gains -> Dist scale: {chassis_ctrl.distance_trim}, Turn scale: {chassis_ctrl.turn_trim}")
        print("[Main] ════════════════════════════════════════\n")

        for side_idx, side_name in enumerate(cardinal_sides):
            print(f"[Main] ── Side {side_idx + 1}/4 ({side_name.upper()}) ──────────────")

            for tile_idx in range(TILES_PER_SIDE):
                label = f"s{side_idx+1}_{side_name}_t{tile_idx+1}"

                recorder.set_phase(label + "_move")
                print(f"[Main]   ➜ Moving {MOVE_DIST} m forward...")
                chassis_ctrl.move_forward(speed=speed, distance=MOVE_DIST)

                recorder.set_phase(label + "_stop")
                print(f"[Main]   ■ Stopping for {STOP_TIME} s...")
                time.sleep(STOP_TIME)

            turn_label = f"s{side_idx+1}_{side_name}_turn_right"
            recorder.set_phase(turn_label)
            print("[Main]   ↻ Turning right 90°...")
            chassis_ctrl.turn_right(speed=TURN_SPEED, degrees=abs(TURN_DEG))

        recorder.set_phase("complete")
        print("\n[Main] ✓ Square path completed successfully!")

    except KeyboardInterrupt:
        print("\n[Main] Program stopped by user.")
    except Exception as err:
        print(f"[Main] Error occurred: {err}")
    finally:
        stop_event.set()
        if rec_thread is not None:
            rec_thread.join(timeout=2.0)

        try:
            ep_robot.chassis.unsub_imu()
            ep_robot.chassis.unsub_position()
            ep_robot.chassis.unsub_attitude()
        except Exception:
            pass

        logger.close()

        print("\n[Main] Generating plots...")
        try:
            from analysis.plot_sensor import plot_sensor_data
            out = plot_sensor_data(logger.filepath)
            if out:
                print(f"[Main] Output plots saved to: {out}")
        except Exception as plot_err:
            print(f"[Main] Failed to generate plots: {plot_err}")

        print("[Main] Releasing robot resources...")
        try:
            ep_robot.close()
        except Exception:
            pass
        print("[Main] Disconnected cleanly.")


if __name__ == "__main__":
    main()
