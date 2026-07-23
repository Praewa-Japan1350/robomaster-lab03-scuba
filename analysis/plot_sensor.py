import os
import glob
from typing import Optional, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt


# Visualization tool for plotting telemetry logs and network latency
class TelemetryPlotter:

    def __init__(self, output_dir: Optional[str] = None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        if output_dir is None:
            self.output_dir = os.path.join(project_root, "analysis", "plots")
        else:
            self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # Locates the latest CSV log file in target directory
    @staticmethod
    def find_latest_csv(search_dir: Optional[str] = None) -> Optional[str]:
        # Determine candidate search paths relative to script location and current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        candidate_dirs = [
            search_dir,
            os.path.join(project_root, "data", "raw", "run1"),
            os.path.join(project_root, "data", "raw"),
            "data/raw/run1",
            "data/raw"
        ]
        
        files = []
        for d in candidate_dirs:
            if d and os.path.isdir(d):
                files.extend(glob.glob(os.path.join(d, "*.csv")))
                files.extend(glob.glob(os.path.join(d, "square_path_*.csv")))
                
        # Deduplicate files
        files = list(set(files))
        if not files:
            print(f"[TelemetryPlotter] No CSV files found in candidate directories.")
            return None
import os
import glob
from typing import Optional, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt


# Visualization tool for plotting telemetry logs and network latency
class TelemetryPlotter:

    def __init__(self, output_dir: Optional[str] = None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        if output_dir is None:
            self.output_dir = os.path.join(project_root, "analysis", "plots")
        else:
            self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # Locates the latest CSV log file in target directory
    @staticmethod
    def find_latest_csv(search_dir: Optional[str] = None) -> Optional[str]:
        # Determine candidate search paths relative to script location and current directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        
        candidate_dirs = [
            search_dir,
            os.path.join(project_root, "data", "raw", "run1"),
            os.path.join(project_root, "data", "raw"),
            "data/raw/run1",
            "data/raw"
        ]
        
        files = []
        for d in candidate_dirs:
            if d and os.path.isdir(d):
                files.extend(glob.glob(os.path.join(d, "*.csv")))
                files.extend(glob.glob(os.path.join(d, "square_path_*.csv")))
                
        # Deduplicate files
        files = list(set(files))
        if not files:
            print(f"[TelemetryPlotter] No CSV files found in candidate directories.")
            return None
            
        # Prefer sensor log files (files not containing 'latency' in filename)
        sensor_files = [f for f in files if "latency" not in os.path.basename(f).lower()]
        target_files = sensor_files if sensor_files else files
        return max(target_files, key=os.path.getctime)

    # Generates multi-panel figures from telemetry dataset
    def generate_report(self, csv_path: Optional[str] = None, output_name: Optional[str] = None) -> Optional[str]:
        if csv_path is None:
            csv_path = self.find_latest_csv()
            if not csv_path:
                return None

        print(f"[TelemetryPlotter] Processing log: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
        except Exception as err:
            print(f"[TelemetryPlotter] CSV read failure: {err}")
            return None

        # Auto-map column aliases if present
        if "step" not in df.columns:
            if "time_step" in df.columns:
                df["step"] = df["time_step"]
            else:
                df["step"] = df.index
        if "phase" not in df.columns and "action" in df.columns:
            df["phase"] = df["action"]

        base_name = os.path.splitext(os.path.basename(csv_path))[0].lower()
        is_latency_log = "latency" in base_name or (output_name and "latency" in output_name.lower())

        # Determine output filename
        if output_name:
            out_filename = output_name if output_name.endswith(".png") else f"{output_name}.png"
        elif is_latency_log:
            out_filename = "latency_plots.png"
        elif "lab1" in base_name or "sensor" in base_name:
            out_filename = "sensor_data_plots.png"
        else:
            out_filename = f"{base_name}_plots.png"

        # Extract phase transition boundaries
        transitions = []
        if "phase" in df.columns and "step" in df.columns:
            prev_phase = None
            for _, row in df.iterrows():
                p = row["phase"]
                if p != prev_phase:
                    transitions.append((row["step"], p))
                    prev_phase = p

        if is_latency_log:
            # Latency Report: Single graph panel
            fig, ax = plt.subplots(figsize=(12, 6))
            fig.suptitle("RoboMaster Connection Latency (RTT)", fontsize=15, fontweight="bold")

            if "latency_ms" in df.columns:
                avg_lat = df["latency_ms"].mean()
                ax.plot(df["step"], df["latency_ms"], color="#d9534f", linewidth=1.8, label="RTT Latency (ms)")
                ax.axhline(
                    y=avg_lat, color="#b52b27", linestyle="--", linewidth=1.4,
                    label=f"Average: {avg_lat:.2f} ms"
                )
                ax.set_title("Connection Latency RTT", fontsize=11, fontweight="bold")
                ax.set_ylabel("Latency (ms)", fontsize=9)
                ax.grid(True, linestyle=":", alpha=0.6)
                ax.legend(loc="upper right", fontsize=9)

                for s_val, _ in transitions:
                    ax.axvline(x=s_val, color="#888888", linestyle=":", alpha=0.35)
            else:
                ax.text(0.5, 0.5, "Latency Data N/A", ha="center", va="center", color="#999999")

            ax.set_xlabel("Time Step (Sample Index)", fontsize=10)
            plt.tight_layout(rect=[0, 0, 1, 0.95])
        else:
            # Sensor Data Report: Exactly 12 channels (4x3 grid)
            fig = plt.figure(figsize=(15, 12))
            fig.suptitle("RoboMaster EP Sensor Data", fontsize=15, fontweight="bold")

            # Plot config: (row, col, col_name, title, y_label, color)
            channels: List[Tuple[int, int, str, str, str, str]] = [
                (0, 0, "acc_x", "Acceleration X", "Acc (m/s²)", "#d9534f"),
                (0, 1, "acc_y", "Acceleration Y", "Acc (m/s²)", "#f0ad4e"),
                (0, 2, "acc_z", "Acceleration Z", "Acc (m/s²)", "#e67e22"),
                (1, 0, "gyro_x", "Angular Velocity X", "Gyro (rad/s)", "#5cb85c"),
                (1, 1, "gyro_y", "Angular Velocity Y", "Gyro (rad/s)", "#2ecc71"),
                (1, 2, "gyro_z", "Angular Velocity Z", "Gyro (rad/s)", "#1abc9c"),
                (2, 0, "pos_x", "Position X (Longitudinal)", "Pos (m)", "#0275d8"),
                (2, 1, "pos_y", "Position Y (Lateral)", "Pos (m)", "#3498db"),
                (2, 2, "pos_z", "Position Z (Vertical)", "Pos (m)", "#9b59b6"),
                (3, 0, "yaw", "Attitude Yaw", "Angle (°)", "#6f42c1"),
                (3, 1, "pitch", "Attitude Pitch", "Angle (°)", "#495057"),
                (3, 2, "roll", "Attitude Roll", "Angle (°)", "#6c757d"),
            ]

            # Render 12 sensor channels in 4x3 grid
            for r, c, col_name, title, ylabel, color in channels:
                ax = plt.subplot2grid((4, 3), (r, c))
                if col_name in df.columns:
                    ax.plot(df["step"], df[col_name], color=color, linewidth=1.4)
                    ax.set_title(title, fontsize=10, fontweight="bold")
                    ax.set_ylabel(ylabel, fontsize=9)
                    ax.grid(True, linestyle=":", alpha=0.6)

                    for s_val, p_name in transitions:
                        ax.axvline(x=s_val, color="#888888", linestyle=":", alpha=0.35)
                        if r == 0 and c == 0:
                            if "Move_Forward" in str(p_name):
                                leg_num = p_name.split("_")[1] if "_" in str(p_name) else p_name
                                lbl = f"Leg {leg_num}"
                                ax.text(
                                    s_val, ax.get_ylim()[1] * 0.9, f" {lbl}",
                                    rotation=0, va="top", ha="left", fontsize=8, fontweight="bold", color="#b52b27"
                                )
                else:
                    ax.text(0.5, 0.5, "N/A", ha="center", va="center", color="#999999")
                    ax.set_title(title, fontsize=10, fontweight="bold")

                if r == 3:
                    ax.set_xlabel("Time Step (Sample Index)", fontsize=9)

            plt.tight_layout(rect=[0, 0, 1, 0.95])

        out_path = os.path.join(self.output_dir, out_filename)
        plt.savefig(out_path, dpi=150)
        plt.close()

        print(f"[TelemetryPlotter] Saved visualization: {out_path}")
        if "latency_ms" in df.columns:
            print(f"[TelemetryPlotter] Mean latency: {df['latency_ms'].mean():.2f} ms")

        return out_path


# Backwards compatible entry function
def plot_sensor_data(csv_path: Optional[str] = None, output_name: Optional[str] = None) -> Optional[str]:
    plotter = TelemetryPlotter()
    return plotter.generate_report(csv_path, output_name)


if __name__ == "__main__":
    import sys
    csv_arg = sys.argv[1] if len(sys.argv) > 1 else None
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None

    plotter = TelemetryPlotter()
    if csv_arg:
        plotter.generate_report(csv_arg, out_arg)
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        lab1_path = os.path.join(project_root, "data", "raw", "run1", "lab1_sensor_data.csv")
        lab2_path = os.path.join(project_root, "data", "raw", "run1", "lab2_latency.csv")

        if os.path.exists(lab1_path):
            plotter.generate_report(lab1_path, "sensor_data_plots.png")
        if os.path.exists(lab2_path):
            plotter.generate_report(lab2_path, "latency_plots.png")
