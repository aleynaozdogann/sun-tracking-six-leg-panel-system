import os
import numpy as np
import pandas as pd

from kinematics import get_bpts, get_ipts, get_panel, max_s


def generate_dataset(output_path="../data/solar_tracking_dataset.csv", total_frames=200):
    bpts = get_bpts()
    records = []

    max_tilt_deg = np.degrees(max_s)

    for frame in range(total_frames):
        # random sun vector
        sx = np.random.uniform(-1, 1)
        sy = np.random.uniform(-1, 1)
        sz = np.random.uniform(0, 1)  # güneş yukarıda

        # normalize
        norm = np.linalg.norm([sx, sy, sz])
        sx, sy, sz = sx / norm, sy / norm, sz / norm


        sun = np.array([sx * 120, sy * 120, sz * 120])

        # Panel points and panel geometry
        sun_norm = sun / np.linalg.norm(sun)

        required_deg = np.degrees(np.arccos(np.clip(sun_norm[2], -1.0, 1.0)))
        tilt_deg = required_deg
        status = "TRACKING" if required_deg < max_tilt_deg else "OUT OF RANGE"



        records.append({
            "frame": frame,
            "sun_x": sx,
            "sun_y": sy,
            "sun_z": sz,
            "required_zenith_deg": required_deg,
            "panel_zenith_deg": tilt_deg,
            "max_zenith_deg": max_tilt_deg,
            "status": status,

        })

    df = pd.DataFrame(records)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Dataset saved to: {output_path}")
    print(df.head())
    return df


if __name__ == "__main__":
    generate_dataset()