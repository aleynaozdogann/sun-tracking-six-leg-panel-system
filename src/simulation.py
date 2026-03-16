import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import joblib
from kinematics import get_bpts, get_ipts, get_panel, br, max_s

model = joblib.load("solar_tracking_model.pkl")
print("Loaded model:", model)
print("Model type:", type(model))

def predict_panel_zenith(sx,sy,sz):
    x = np.array([[sx,sy,sz]])
    pred = model.predict(x)[0]
    return pred

def build_ml_target_vector(sx,sy,sz,predicted_zenith_deg,radius=120):
    azimuth = np.arctan2(sy,sx)
    zenith_rad =np.radians(predicted_zenith_deg)

    new_sx = radius * np.sin(zenith_rad) * np.cos(azimuth)
    new_sy = radius * np.sin(zenith_rad) * np.sin(azimuth)
    new_sz = radius * np.cos(zenith_rad)

    return np.array([new_sx,new_sy,new_sz])




def run_simulation():
    fig = plt.figure(figsize=(13, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_zlim(0, 130)

    # Base Disk
    theta = np.linspace(0, 2 * np.pi, 60)
    r = np.linspace(0, br, 20)
    T, R = np.meshgrid(theta, r)
    ax.plot_surface(
        R * np.cos(T),
        R * np.sin(T),
        np.zeros_like(R),
        color='lightgreen',
        alpha=0.25
    )

    bpts = get_bpts()

    # Objects
    sun_scatter = ax.scatter([], [], [], c='orange', s=400, edgecolors='yellow')
    ipts_scatter = ax.scatter([], [], [], c='black', s=25)

    link_colors = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1)
    ]

    leg_lines = []
    for k in range(3):
        ln, = ax.plot([], [], [], color=link_colors[k], linewidth=2)
        leg_lines.append(ln)

    # Text blocks
    sun_text = ax.text2D(
        1.05, 0.95, "", transform=ax.transAxes,
        fontsize=12, va='top', color='orange'
    )

    leg_texts = []
    y_positions = [0.88, 0.66, 0.44]
    for k in range(3):
        t = ax.text2D(
            1.05, y_positions[k], "", transform=ax.transAxes,
            fontsize=10, va='top', color=link_colors[k]
        )
        leg_texts.append(t)

    tilt_text = ax.text2D(
        1.05, 0.22, "", transform=ax.transAxes,
        fontsize=12, va='top', color='red'
    )

    panel_surf = None

    def update(frame):
        nonlocal panel_surf

        total = 200
        ang = (frame - total / 2) / (total / 2)

        # Sun
        sx = -120 * np.sin(ang)
        sy = -80 * np.sin(ang)
        sz = 120 * np.cos(ang)
        sun = np.array([sx, sy, sz])
        sun_norm = sun / np.linalg.norm(sun)
        required_deg = np.degrees(np.arccos(sun_norm[2]))
        predicted_deg = predict_panel_zenith(sx,sy,sz)
        max_tilt_deg = np.degrees(max_s)
        predicted_deg = np.clip(predicted_deg, 0, max_tilt_deg)
        ml_sun = build_ml_target_vector(
            sx,sy,sz,
            predicted_deg,
            radius = np.linalg.norm(sun)
        )

        ipts = get_ipts(ml_sun)
        real_normal, normal, PX, PY, PZ = get_panel(ipts, ml_sun)

        tilt_deg = np.degrees(np.arccos(normal[2]))
        status = "TRACKING" if required_deg < max_tilt_deg else "OUT OF RANGE"

        if status == "OUT OF RANGE":
            gray = "gray"
            panel_color = "gray"
            tilt_text.set_color(gray)
            sun_text.set_color(gray)
            ipts_scatter.set_color(gray)

            for k in range(3):
                leg_texts[k].set_color(gray)
                leg_lines[k].set_color(gray)
        else:
            panel_color = "dodgerblue"
            tilt_text.set_color("red")
            sun_text.set_color("orange")
            ipts_scatter.set_color("black")

            for k in range(3):
                leg_texts[k].set_color(link_colors[k])
                leg_lines[k].set_color(link_colors[k])

        # Update scatters
        sun_scatter._offsets3d = ([sx], [sy], [sz])
        ipts_scatter._offsets3d = (ipts[:, 0], ipts[:, 1], ipts[:, 2])

        # Leg lines + text
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

            right_len = np.linalg.norm(panel_pt - base)
            left_len = np.linalg.norm(next_base - panel_pt)

            leg_texts[k].set_text(
                f"Right Leg = {right_len:.2f}\n"
                f" Base = ({base[0]:6.1f}, {base[1]:6.1f}, {base[2]:4.1f})\n"
                f" Panel = ({panel_pt[0]:6.1f}, {panel_pt[1]:6.1f}, {panel_pt[2]:4.1f})\n"
                f"Left Leg = {left_len:.2f}\n"
                f" Panel = ({panel_pt[0]:6.1f}, {panel_pt[1]:6.1f}, {panel_pt[2]:4.1f})\n"
                f" NextBase = ({next_base[0]:6.1f}, {next_base[1]:6.1f}, {next_base[2]:4.1f})"
            )

        # Redraw panel
        if panel_surf is not None:
            panel_surf.remove()

        panel_surf = ax.plot_surface(
            PX, PY, PZ,
            color=panel_color,
            alpha=1,
            linewidth=0.5
        )

        tilt_text.set_text(
            f"Max Zenith: {max_tilt_deg:5.2f}\n"
            f"Predicted Zenith: {predicted_deg:5.2f}\n"
            f"Panel Zenith: {tilt_deg:5.2f}\n"
            f"Required Zenith: {required_deg:5.2f}\n"
            f"Status: {status}"
        )

        sun_text.set_text(
            f"Sun = ({sx:6.1f}, {sy:6.1f}, {sz:6.1f})"
        )

        return leg_lines + [sun_scatter, ipts_scatter, panel_surf] + leg_texts + [sun_text, tilt_text]

    ani = animation.FuncAnimation(fig, update, frames=200, interval=70)

    plt.tight_layout()
    plt.show()

