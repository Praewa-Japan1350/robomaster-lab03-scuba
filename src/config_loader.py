# src/config_loader.py
# ฟังก์ชันสำหรับอ่านและแปลงไฟล์ settings.yaml เป็น Dictionary (Parser function)

import os
import yaml


def load_settings(config_path=None):
    """
    โหลดไฟล์ settings.yaml แล้วแปลงเป็น Python Dictionary

    Parameters
    ----------
    config_path : str, optional
        พาธไปยังไฟล์ YAML  (ค่าเริ่มต้นคือ config/settings.yaml)

    Returns
    -------
    dict
        Dictionary ที่มีค่าตั้งค่าทั้งหมดจากไฟล์ YAML
    """
    if config_path is None:
        # หาโฟลเดอร์ root ของโปรเจกต์ (ขึ้นไป 1 ระดับจาก src/)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, "config", "settings.yaml")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        print(f"[ConfigLoader] Loaded settings from: {config_path}")
        return config

    except FileNotFoundError:
        print(f"[ConfigLoader] ERROR: ไม่พบไฟล์ {config_path}")
        raise
    except yaml.YAMLError as e:
        print(f"[ConfigLoader] ERROR: ไฟล์ YAML มีรูปแบบไม่ถูกต้อง — {e}")
        raise
