import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import joblib
import itertools
import requests


from kinematics import get_bpts, get_ipts, get_panel, br, max_s

leg_names = ["RED", "GREEN", "BLUE"]

# -------------------------
# Model Load
# -------------------------
model = joblib.load("solar_tracking_model.pkl")
print("Loaded model:", model)
print("Model type:", type(model))

# -------------------------
# Leg Constraints
# -------------------------
LEG_MIN = 40
LEG_MAX = 140


# -------------------------
# ML Prediction
# -------------------------
def predict_panel_zenith(sx, sy, sz):
    url = "http://127.0.0.1:8000/predict"

    payload = {
        "sun_x": sx,
        "sun_y": sy,
        "sun_z": sz
    }

    response = requests.post(url, json=payload)

    prediction = response.json()["predicted_zenith"]
    return prediction




def build_ml_target_vector(sx, sy, sz, predicted_zenith_deg, radius=120):
    azimuth = np.arctan2(sy, sx)
    zenith_rad = np.radians(predicted_zenith_deg)

    new_sx = radius * np.sin(zenith_rad) * np.cos(azimuth)
    new_sy = radius * np.sin(zenith_rad) * np.sin(azimuth)
    new_sz = radius * np.cos(zenith_rad)

    return np.array([new_sx, new_sy, new_sz])


# -------------------------
# Leg Length Check
# -------------------------
def compute_leg_lengths(bpts, ipts):
    lengths = []
    for k in range(3):
        base = bpts[k]
        panel_pt = ipts[k]
        next_base = bpts[(k + 1) % 3]

        right_len = np.linalg.norm(panel_pt - base)
        left_len = np.linalg.norm(next_base - panel_pt)

        lengths.append((right_len, left_len))
    return lengths


def check_leg_constraints(lengths, leg_min=LEG_MIN, leg_max=LEG_MAX):
    for right_len, left_len in lengths:
        if not (leg_min <= right_len <= leg_max):
            return False
        if not (leg_min <= left_len <= leg_max):
            return False
    return True

def get_leg_status_messages(lengths, leg_min=LEG_MIN, leg_max=LEG_MAX):
    messages = []
    leg_names = ["RED", "GREEN", "BLUE"]

    for k, (right_len, left_len) in enumerate(lengths):
        name = leg_names[k]

        if right_len < leg_min:
            messages.append(f"{name} Right: SHORT")
        elif right_len > leg_max:
            messages.append(f"{name} Right: LONG")

        if left_len < leg_min:
            messages.append(f"{name} Left: SHORT")
        elif left_len > leg_max:
            messages.append(f"{name} Left: LONG")

    if not messages:
        messages.append("All legs OK")

    return messages


# -------------------------
# Main Simulation
# -------------------------
def run_simulation():
    fig = plt.figure(figsize=(13, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_zlim(0, 130)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("ML-Based Solar Tracking with Leg-Length Constraints")

    # -------------------------
    # Base disk
    # -------------------------
    theta = np.linspace(0, 2 * np.pi, 60)
    r = np.linspace(0, br, 20)
    T, R = np.meshgrid(theta, r)

    ax.plot_surface(
        R * np.cos(T),
        R * np.sin(T),
        np.zeros_like(R),
        color="lightgreen",
        alpha=0.25
    )

    bpts = get_bpts()

    # -------------------------
    # Static base points
    # -------------------------
    ax.scatter(bpts[:, 0], bpts[:, 1], bpts[:, 2], c="darkgreen", s=40, label="Base Points")

    # -------------------------
    # Objects
    # -------------------------
    sun_scatter = ax.scatter([], [], [], c="orange", s=400, edgecolors="yellow")
    ipts_scatter = ax.scatter([], [], [], c="black", s=25)

    link_colors = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1)
    ]

    leg_lines = []
    for k in range(3):
        ln, = ax.plot([], [], [], color=link_colors[k], linewidth=2)
        leg_lines.append(ln)



    # -------------------------
    # Text blocks
    # -------------------------
    sun_text = ax.text2D(
        1.05, 0.95, "", transform=ax.transAxes,
        fontsize=10, va="top", color="orange"
    )

    leg_texts = []
    y_positions = [0.90, 0.75, 0.60]

    for k in range(3):
        t = ax.text2D(
            1.05, y_positions[k], "", transform=ax.transAxes,
            fontsize=9, va="top", color=link_colors[k]
        )
        leg_texts.append(t)

    tilt_text = ax.text2D(
        1.05, 0.35, "", transform=ax.transAxes,
        fontsize=10, va="top", color="red"
    )

    constraint_text = ax.text2D(
        1.05, 0.10, "", transform=ax.transAxes,
        fontsize=9, va="top", color="purple"
    )

    panel_surf = None

    last_valid_ipts = None
    last_valid_PX = None
    last_valid_PY = None
    last_valid_PZ = None
    last_valid_tilt_deg = None
    last_valid_leg_lengths = None

    locked_out = False
    current_cycle = -1
    seen_valid_in_cycle = False

    def update(frame):
        nonlocal panel_surf
        nonlocal last_valid_ipts, last_valid_PX, last_valid_PY, last_valid_PZ
        nonlocal last_valid_tilt_deg, last_valid_leg_lengths
        nonlocal locked_out, current_cycle, seen_valid_in_cycle

        total = 200
        cycle = frame // total
        local_frame = frame % total

        if cycle != current_cycle:
            current_cycle = cycle
            locked_out = False
            seen_valid_in_cycle = False

            last_valid_ipts = None
            last_valid_PX = None
            last_valid_PY = None
            last_valid_PZ = None
            last_valid_tilt_deg = None
            last_valid_leg_lengths = None

        ang = (local_frame - total / 2) / (total / 2)

        # -------------------------
        # Sun position
        # -------------------------
        sx = -120 * np.sin(ang)
        sy = -80 * np.sin(ang)
        sz = 120 * np.cos(ang)

        sun = np.array([sx, sy, sz])
        sun_norm = sun / np.linalg.norm(sun)

        required_deg = np.degrees(np.arccos(np.clip(sun_norm[2], -1.0, 1.0)))
        max_tilt_deg = np.degrees(max_s)

        # -------------------------
        # ML prediction
        # -------------------------
        predicted_deg = predict_panel_zenith(sx, sy, sz)
        predicted_deg = np.clip(predicted_deg, 0, max_tilt_deg)

        ml_sun = build_ml_target_vector(
            sx, sy, sz,
            predicted_deg,
            radius=np.linalg.norm(sun)
        )

        # -------------------------
        # Geometry
        # -------------------------
        ipts = get_ipts(ml_sun)
        real_normal, normal, PX, PY, PZ = get_panel(ipts, ml_sun)

        tilt_deg = np.degrees(np.arccos(np.clip(normal[2], -1.0, 1.0)))

        # -------------------------
        # Constraint checks
        # -------------------------
        leg_lengths = compute_leg_lengths(bpts, ipts)
        legs_valid = check_leg_constraints(leg_lengths)
        leg_status_messages = get_leg_status_messages(leg_lengths)
        sun_valid = required_deg < max_tilt_deg
        print(
            f"frame={frame}, cycle={cycle}, local={local_frame}, "
            f"sun_valid={sun_valid}, legs_valid={legs_valid}, locked_out={locked_out}"
        )

        current_valid = sun_valid and legs_valid
        fail_reason = None

        if not sun_valid:
            fail_reason = "SUN_LIMIT"
        elif not legs_valid:
            fail_reason = "LEG_LIMIT"

        if not locked_out:
            if current_valid:
                status = "TRACKING"
                seen_valid_in_cycle = True

                last_valid_ipts = ipts.copy()
                last_valid_PX = PX.copy()
                last_valid_PY = PY.copy()
                last_valid_PZ = PZ.copy()
                last_valid_tilt_deg = tilt_deg
                last_valid_leg_lengths = list(leg_lengths)

            else:
                if not seen_valid_in_cycle:
                    status = "WAITING"
                else:
                    status = "LOCKED"

                    if last_valid_ipts is not None:
                        locked_out = True
                        ipts = last_valid_ipts
                        PX = last_valid_PX
                        PY = last_valid_PY
                        PZ = last_valid_PZ
                        tilt_deg = last_valid_tilt_deg
                        leg_lengths = list(last_valid_leg_lengths)

        else:
            status = "LOCKED"

            if last_valid_ipts is not None:
                ipts = last_valid_ipts
                PX = last_valid_PX
                PY = last_valid_PY
                PZ = last_valid_PZ
                tilt_deg = last_valid_tilt_deg
                leg_lengths = list(last_valid_leg_lengths)
        # -------------------------
        # Color logic
        # -------------------------
        if status == "LOCKED":
            if fail_reason == "LEG_LIMIT":
                panel_color = "red"  # 🔥 bacak problemi
            elif fail_reason == "SUN_LIMIT":
                panel_color = "gray"  # 🌑 güneş limiti
            else:
                panel_color = "gray"

            tilt_text.set_color("gray")
            sun_text.set_color("gray")
            ipts_scatter.set_color("gray")
            constraint_text.set_color("gray")

            for k in range(3):
                leg_texts[k].set_color("gray")
                leg_lines[k].set_color("gray")

        elif status == "WAITING":
            panel_color = "lightsteelblue"

            tilt_text.set_color("purple")
            sun_text.set_color("orange")
            ipts_scatter.set_color("black")
            constraint_text.set_color("purple")

            for k in range(3):
                leg_texts[k].set_color(link_colors[k])
                leg_lines[k].set_color(link_colors[k])

        else:  # TRACKING
            panel_color = "dodgerblue"

            tilt_text.set_color("red")
            sun_text.set_color("orange")
            ipts_scatter.set_color("black")
            constraint_text.set_color("purple")

            for k in range(3):
                leg_texts[k].set_color(link_colors[k])
                leg_lines[k].set_color(link_colors[k])

        # -------------------------
        # Update scatters
        # -------------------------
        sun_scatter._offsets3d = ([sx], [sy], [sz])
        ipts_scatter._offsets3d = (ipts[:, 0], ipts[:, 1], ipts[:, 2])

        # -------------------------
        # Update leg lines + text
        # -------------------------
        for k in range(3):
            base = bpts[k]
            panel_pt = ipts[k]
            next_base = bpts[(k + 1) % 3]

            leg_lines[k].set_data(
                [base[0], panel_pt[0], next_base[0]],
                [base[1], panel_pt[1], next_base[1]]
            )
            leg_lines[k].set_3d_properties(
                [base[2], panel_pt[2], next_base[2]]
            )

            right_len, left_len = leg_lengths[k]

            right_ok = LEG_MIN <= right_len <= LEG_MAX
            left_ok = LEG_MIN <= left_len <= LEG_MAX

            name = leg_names[k]

            leg_texts[k].set_text(
                f"{name} LEG\n"
                f"R: {right_len:.1f} ({'OK' if right_ok else 'X'})\n"
                f"L: {left_len:.1f} ({'OK' if left_ok else 'X'})"
            )

        # -------------------------
        # Redraw panel
        # -------------------------
        if panel_surf is not None:
            panel_surf.remove()

        panel_surf = ax.plot_surface(
            PX, PY, PZ,
            color=panel_color,
            alpha=1,
            linewidth=0.5
        )

        # -------------------------
        # Info text
        # -------------------------
        tilt_text.set_text(
            f"Max Zenith: {max_tilt_deg:5.2f}\n"
            f"Predicted Zenith: {predicted_deg:5.2f}\n"
            f"Panel Zenith: {tilt_deg:5.2f}\n"
            f"Required Zenith: {required_deg:5.2f}\n"
            f"Sun Valid: {sun_valid}\n"
            f"Legs Valid: {legs_valid}\n"
            f"Leg Range: [{LEG_MIN}, {LEG_MAX}]\n"
            f"Status: {status}"
        )
        extra = f"\nFail: {fail_reason}" if fail_reason else ""

        constraint_text.set_text(
            "Constraint Info:\n" +
            "\n".join(leg_status_messages) +
            extra
        )

        sun_text.set_text(
            f"Sun = ({sx:6.1f}, {sy:6.1f}, {sz:6.1f})"
        )

        print(
            f"Cycle {cycle} | LocalFrame {local_frame:03d} | " 
            f"Pred={predicted_deg:.2f} | "
            f"Req={required_deg:.2f} | "
            f"Panel={tilt_deg:.2f} | "
            f"Legs={[(round(r, 2), round(l, 2)) for r, l in leg_lengths]} | "
            f"SunValid={sun_valid} | LegsValid={legs_valid} | Status={status}"
        )

        return leg_lines + [sun_scatter, ipts_scatter, panel_surf] + leg_texts + [sun_text, tilt_text, constraint_text]

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=itertools.count(),
        interval=70,
        repeat=False
    )

    plt.tight_layout()
    plt.show()