import os
import glob
from typing import Optional, List, Tuple
import pandas as pd
import matplotlib.pyplot as plt


# Visualization tool for plotting telemetry logs and network latency
class TelemetryPlotter:

    def __init__(self, output_dir: str = "analysis/plots"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    # Locates the latest CSV log file in target directory
    @staticmethod
    def find_latest_csv(search_dir: str = "data/raw/run1") -> Optional[str]:
        pattern = os.path.join(search_dir, "square_path_*.csv")
        files = glob.glob(pattern)
        if not files:
            print(f"[TelemetryPlotter] No CSV files matching '{pattern}'")
            return None
        return max(files, key=os.path.getctime)

    # Generates multi-panel figures from telemetry dataset
    def generate_report(self, csv_path: Optional[str] = None) -> Optional[str]:
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

        # Verify required data columns
        required_cols = [
            "step", "phase", "acc_x", "acc_y", "acc_z",
            "gyro_x", "gyro_y", "gyro_z", "pos_x", "pos_y",
            "pos_z", "yaw", "pitch", "roll", "latency_ms"
        ]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"[TelemetryPlotter] Missing columns: {missing}")

        # Setup figure canvas
        fig = plt.figure(figsize=(15, 16))
        fig.suptitle(
            f"RoboMaster EP Telemetry & RTT Latency\nSource: {os.path.basename(csv_path)}",
            fontsize=15,
            fontweight="bold"
        )

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

        # Extract phase transition boundaries
        transitions = []
        if "phase" in df.columns and "step" in df.columns:
            prev_phase = None
            for _, row in df.iterrows():
                p = row["phase"]
                if p != prev_phase:
                    transitions.append((row["step"], p))
                    prev_phase = p

        # Render 12 sensor channels
        for r, c, col_name, title, ylabel, color in channels:
            ax = plt.subplot2grid((5, 3), (r, c))
            if col_name in df.columns:
                ax.plot(df["step"], df[col_name], color=color, linewidth=1.4)
                ax.set_title(title, fontsize=10, fontweight="bold")
                ax.set_ylabel(ylabel, fontsize=9)
                ax.grid(True, linestyle=":", alpha=0.6)

                for s_val, p_name in transitions:
                    ax.axvline(x=s_val, color="#888888", linestyle=":", alpha=0.35)
                    if r == 0 and c == 0:
                        lbl = p_name.replace("square_path_", "")
                        ax.text(
                            s_val, ax.get_ylim()[1], f" {lbl}",
                            rotation=90, va="top", fontsize=7, color="#666666"
                        )
            else:
                ax.text(0.5, 0.5, "N/A", ha="center", va="center", color="#999999")
                ax.set_title(title, fontsize=10, fontweight="bold")

        # Render connection latency timeline across full width
        ax_lat = plt.subplot2grid((5, 3), (4, 0), colspan=3)
        if "latency_ms" in df.columns:
            avg_lat = df["latency_ms"].mean()
            ax_lat.plot(df["step"], df["latency_ms"], color="#d9534f", linewidth=1.8, label="RTT Latency (ms)")
            ax_lat.axhline(
                y=avg_lat, color="#b52b27", linestyle="--", linewidth=1.4,
                label=f"Average: {avg_lat:.2f} ms"
            )
            ax_lat.set_title("Connection Latency RTT", fontsize=11, fontweight="bold")
            ax_lat.set_ylabel("Latency (ms)", fontsize=9)
            ax_lat.grid(True, linestyle=":", alpha=0.6)
            ax_lat.legend(loc="upper right", fontsize=9)

            for s_val, _ in transitions:
                ax_lat.axvline(x=s_val, color="#888888", linestyle=":", alpha=0.35)
        else:
            ax_lat.text(0.5, 0.5, "Latency N/A", ha="center", va="center", color="#999999")

        ax_lat.set_xlabel("Time Step (Sample Index)", fontsize=10)
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        # Export figure
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        out_path = os.path.join(self.output_dir, f"{base_name}_plots.png")
        plt.savefig(out_path, dpi=150)
        plt.close()

        print(f"[TelemetryPlotter] Saved visualization: {out_path}")
        if "latency_ms" in df.columns:
            print(f"[TelemetryPlotter] Mean latency: {df['latency_ms'].mean():.2f} ms")

        return out_path


# Backwards compatible entry function
def plot_sensor_data(csv_path: Optional[str] = None) -> Optional[str]:
    plotter = TelemetryPlotter()
    return plotter.generate_report(csv_path)


if __name__ == "__main__":
    plot_sensor_data()
