import os
import numpy as np
import pandas as pd

from kinematics import get_bpts, get_ipts, get_panel, max_s


def generate_dataset(output_path="../data/solar_tracking_dataset.csv", total_frames=200):
    bpts = get_bpts()
    records = []

    max_tilt_deg = np.degrees(max_s)

    for frame in range(total_frames):
        ang = (frame - total_frames / 2) / (total_frames / 2)

        # Sun position
        sx = -120 * np.sin(ang)
        sy = -80 * np.sin(ang)
        sz = 120 * np.cos(ang)
        sun = np.array([sx, sy, sz])

        # Panel points and panel geometry
        ipts = get_ipts(sun)
        real_normal, normal, _, _, _ = get_panel(ipts, sun)

        required_deg = np.degrees(np.arccos(real_normal[2]))
        tilt_deg = np.degrees(np.arccos(normal[2]))
        status = "TRACKING" if required_deg < max_tilt_deg else "OUT OF RANGE"

        # Leg lengths
        leg_lengths = []
        for k in range(3):
            base = bpts[k]
            panel_pt = ipts[k]
            length = np.linalg.norm(panel_pt - base)
            leg_lengths.append(length)

        records.append({
            "frame": frame,
            "sun_x": sx,
            "sun_y": sy,
            "sun_z": sz,
            "required_zenith_deg": required_deg,
            "panel_zenith_deg": tilt_deg,
            "max_zenith_deg": max_tilt_deg,
            "status": status,
            "leg_1_length": leg_lengths[0],
            "leg_2_length": leg_lengths[1],
            "leg_3_length": leg_lengths[2],
        })

    df = pd.DataFrame(records)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Dataset saved to: {output_path}")
    print(df.head())
    return df


if __name__ == "__main__":
    generate_dataset()