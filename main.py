import time
import threading
from robomaster import robot
from src.config_loader import load_settings
from src.chassis import ChassisController, get_current_pos, get_current_att, get_current_imu, sub_position_handler, sub_attitude_handler, sub_imu_handler
from src.logger import CSVLogger

def run_lab1_api_testing(ep_robot, config):
    print("\n" + "="*60)
    print("      LAB ASSIGNMENT 1: API TESTING & SENSOR LOGGING")
    print("="*60)
    
    chassis_ctrl = ChassisController(ep_robot)
    
    speed_x = config['robot_params']['chassis'].get('default_speed_x', 0.7)
    speed_z = config['robot_params']['chassis'].get('turn_speed_z', 90)
    tile_size = config['robot_params']['chassis'].get('tile_size', 0.6)
    csv_path = config['paths'].get('lab1_csv', 'data/raw/lab1_sensor_data.csv')
    
    logger = CSVLogger(filepath=csv_path)
    headers = [
        "timestamp", "time_step", "leg", "action", 
        "pos_x", "pos_y", "pos_z", 
        "yaw", "pitch", "roll", 
        "acc_x", "acc_y", "acc_z", 
        "gyro_x", "gyro_y", "gyro_z"
    ]
    logger.start(headers)
    
    chassis_ctrl.start_subscriptions(
        pos_cb=sub_position_handler,
        att_cb=sub_attitude_handler,
        imu_cb=sub_imu_handler,
        freq=10
    )
    time.sleep(0.5)
    
    logging_active = True
    start_time = time.time()
    current_leg = 0
    current_action = "INITIALIZING"
    step_count = 0
    
    def log_worker():
        nonlocal step_count
        while logging_active:
            now = time.time()
            elapsed = round(now - start_time, 3)
            pos = get_current_pos()
            att = get_current_att()
            imu = get_current_imu()
            
            row = [
                round(now, 3), elapsed, current_leg, current_action,
                round(pos['x'], 3), round(pos['y'], 3), round(pos['z'], 3),
                round(att['yaw'], 2), round(att['pitch'], 2), round(att['roll'], 2),
                round(imu['acc_x'], 3), round(imu['acc_y'], 3), round(imu['acc_z'], 3),
                round(imu['gyro_x'], 3), round(imu['gyro_y'], 3), round(imu['gyro_z'], 3)
            ]
            logger.log_row(row)
            
            print(f"[LOG t={elapsed:5.2f}s | Step={step_count:03d} | Leg={current_leg}] "
                  f"Pos:({pos['x']:.2f}, {pos['y']:.2f}, {pos['z']:.2f}) | "
                  f"Att:(Yaw:{att['yaw']:.1f}°) | "
                  f"Action: {current_action}")
            
            step_count += 1
            time.sleep(0.1)
            
    log_thread = threading.Thread(target=log_worker, daemon=True)
    log_thread.start()
    
    try:
        for leg in range(1, 5):
            current_leg = leg
            print(f"\n--- Starting Leg {leg}/4 ---")
            
            # Action A: Move Forward 1 Tile
            current_action = f"Leg_{leg}_Move_Forward"
            chassis_ctrl.move_forward(speed=speed_x, distance=tile_size).wait_for_completed()
            chassis_ctrl.stop()
            
            # Action B: Stop for 1 second at tile center
            current_action = f"Leg_{leg}_Stop_1s"
            print(f"[Main] Reached tile center {leg}. Pausing for 1 second...")
            time.sleep(1.0)
            
            # Action C: Turn Right 90 Degrees
            current_action = f"Leg_{leg}_Turn_Right_90"
            chassis_ctrl.turn_right(speed_z=speed_z, angle=90).wait_for_completed()
            chassis_ctrl.stop()
            time.sleep(0.5)

        current_action = "COMPLETED"
        print("\n[Lab 1] Square path navigation complete!")
        
    finally:
        logging_active = False
        log_thread.join(timeout=2.0)
        chassis_ctrl.stop_subscriptions()
        logger.close()


def run_lab2_connectivity_test(ep_robot, config):
    print("\n" + "="*60)
    print("      LAB ASSIGNMENT 2: CONNECTIVITY & LATENCY TEST")
    print("="*60)
    
    csv_path = config['paths'].get('lab2_csv', 'data/raw/lab2_latency.csv')
    logger = CSVLogger(filepath=csv_path)
    headers = ["iteration", "timestamp", "operation_type", "latency_ms"]
    logger.start(headers)
    
    latencies = []
    num_iterations = 50
    print(f"[Lab 2] Measuring latency over {num_iterations} Read/Write iterations...")
    
    try:
        for i in range(1, num_iterations + 1):
            op_type = "Write_Speed_Command" if i % 2 == 1 else "Read_SN_Info"
            
            t0 = time.perf_counter()
            if op_type == "Write_Speed_Command":
                ep_robot.chassis.drive_speed(x=0, y=0, z=0)
            else:
                _ = ep_robot.get_sn()
            t1 = time.perf_counter()
            
            latency_ms = (t1 - t0) * 1000.0
            latencies.append(latency_ms)
            now = time.time()
            
            logger.log_row([i, round(now, 3), op_type, round(latency_ms, 3)])
            print(f"[Lab 2 | Iteration {i:02d}/{num_iterations}] Op: {op_type:<20} | Latency: {latency_ms:.2f} ms")
            time.sleep(0.05)
            
        avg_lat = sum(latencies) / len(latencies) if latencies else 0
        min_lat = min(latencies) if latencies else 0
        max_lat = max(latencies) if latencies else 0
        
        print("\n" + "-"*40)
        print(f"  CONNECTIVITY TEST SUMMARY")
        print(f"  Average Latency: {avg_lat:.2f} ms")
        print(f"  Min Latency:     {min_lat:.2f} ms")
        print(f"  Max Latency:     {max_lat:.2f} ms")
        print("-" * 40)
        
    finally:
        logger.close()


def main():
    config = load_settings()
    
    print("[Main] Connecting to RoboMaster via Wi-Fi Direct...")
    ep_robot = robot.Robot()
    
    try:
        ep_robot.initialize(conn_type="ap")
        print("[Main] Connected! SN:", ep_robot.get_sn())
        
        run_lab1_api_testing(ep_robot, config)
        run_lab2_connectivity_test(ep_robot, config)
        
    except KeyboardInterrupt:
        print("\n[Main] Execution stopped by user.")
    except Exception as e:
        print(f"[Main] Error occurred: {e}")
    finally:
        print("\n[Main] Releasing robot resources...")
        try:
            ep_robot.camera.stop_video_stream()
        except Exception:
            pass
        try:
            ep_robot.close()
        except Exception:
            pass
        print("[Main] Disconnected cleanly.")

if __name__ == "__main__":
    main()
