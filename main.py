# main.py

import time
from robomaster import robot
from src.config_loader import load_settings


def main():
    # 1. โหลดการตั้งค่าจาก settings.yaml (เช่น ขีดจำกัดความเร็ว)
    config = load_settings()

    # 2. สร้าง instance และสั่งเชื่อมต่อตรงนี้เลย
    print("[Main] Connecting to RoboMaster via Wi-Fi Direct...")
    ep_robot = robot.Robot()

    try:
        # เริ่มต้นเชื่อมต่อ (AP mode คือเชื่อมแบบ Wi-Fi Direct)
        ep_robot.initialize(conn_type="ap")
        print("[Main] Connected! SN:", ep_robot.get_sn())

        # --- เริ่มเขียน Logic ควบคุมหุ่นยนต์ของคุณตรงนี้ ---
        chassis = ep_robot.chassis

        # ดึงความเร็วเริ่มต้นมาจากไฟล์ YAML
        speed = config['robot_params']['chassis']['default_speed_x']

        print(f"[Main] Moving forward at {speed} m/s...")
        chassis.move(x=0.5, y=0, z=0, xy_speed=speed).wait_for_completed()

        time.sleep(1)
        # ------------------------------------------------

    except KeyboardInterrupt:
        print("\n[Main] Program stopped by user.")
    except Exception as e:
        print(f"[Main] Error occurred: {e}")
    finally:
        # 3. บล็อกนี้จะทำงานเสมอเมื่อออกจากบล็อก try เพื่อคืน Resource ให้หุ่นยนต์
        print("[Main] Releasing robot resources...")
        try:
            ep_robot.camera.stop_video_stream()  # ปิดกล้องถ้ามีการเปิดใช้
        except:
            pass
        ep_robot.uninitialize()
        print("[Main] Disconnected cleanly.")


if __name__ == "__main__":
    main()
