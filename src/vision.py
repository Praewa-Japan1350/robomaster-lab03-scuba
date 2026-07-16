# src/vision.py
# คลาสสตรีมภาพและประมวลผลกล้อง (OpenCV)

import cv2


class VisionController:
    """
    คลาสสำหรับจัดการสตรีมวิดีโอจากกล้องของ RoboMaster EP
    รองรับการเปิด/ปิดสตรีม, ดึงเฟรม, และแสดงภาพผ่าน OpenCV
    """

    def __init__(self, ep_robot):
        """
        Parameters
        ----------
        ep_robot : robomaster.robot.Robot
            instance ของหุ่นยนต์ที่เชื่อมต่อแล้ว
        """
        self.camera = ep_robot.camera
        self._streaming = False
        print("[Vision] Initialized")

    def start_stream(self):
        """เปิดสตรีมวิดีโอจากกล้องหุ่นยนต์"""
        if not self._streaming:
            self.camera.start_video_stream(display=False)
            self._streaming = True
            print("[Vision] Video stream started")

    def stop_stream(self):
        """ปิดสตรีมวิดีโอ"""
        if self._streaming:
            self.camera.stop_video_stream()
            self._streaming = False
            print("[Vision] Video stream stopped")

    def get_frame(self):
        """
        ดึงเฟรมปัจจุบันจากกล้อง

        Returns
        -------
        numpy.ndarray or None
            ภาพเฟรมปัจจุบัน (BGR format) หรือ None ถ้ายังไม่ได้เปิดสตรีม
        """
        if not self._streaming:
            print("[Vision] WARNING: Stream not started. Call start_stream() first.")
            return None
        try:
            frame = self.camera.read_cv2_image(strategy="newest")
            return frame
        except Exception as e:
            print(f"[Vision] ERROR reading frame: {e}")
            return None

    def show_frame(self, frame, window_name="RoboMaster Camera"):
        """
        แสดงเฟรมภาพบนหน้าจอผ่าน OpenCV

        Parameters
        ----------
        frame : numpy.ndarray
            ภาพที่ต้องการแสดง
        window_name : str
            ชื่อหน้าต่างแสดงผล

        Returns
        -------
        bool
            True ถ้ายังแสดงผลอยู่, False ถ้ากด 'q' เพื่อปิด
        """
        if frame is None:
            return True
        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            print("[Vision] User pressed 'q' — closing display.")
            cv2.destroyAllWindows()
            return False
        return True

    def save_frame(self, frame, filepath):
        """บันทึกเฟรมภาพเป็นไฟล์"""
        if frame is not None:
            cv2.imwrite(filepath, frame)
            print(f"[Vision] Frame saved to {filepath}")
