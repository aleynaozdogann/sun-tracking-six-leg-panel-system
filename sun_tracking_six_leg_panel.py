import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

# --- 1. PARAMETERS ---
br = 30.0
pr = 15.0
h = 40.0
max_s = np.arctan(h / br)

# --- BASE POINTS ---
def get_bpts():
    pts = []
    for k in range(3):
        angle = k * (2*np.pi) / 3
        pts.append([br*np.cos(angle), br*np.sin(angle), 0.0])
    return np.array(pts)

# --- HINGE POINTS ON PANEL ---
def get_ipts(sun_pos):
    sx, sy, sz = sun_pos

    vec_z = sz - h
    vec_xy = np.sqrt(sx**2 + sy**2)

    current_tilt = np.arctan2(vec_xy, vec_z)

    if current_tilt > max_s:
        azimuth = np.arctan2(sy, sx)

        new_xy = vec_z * np.tan(max_s)
        sx = new_xy * np.cos(azimuth)
        sy = new_xy * np.sin(azimuth)

    ip = []
    for k in range(3):
        phi = (np.pi/3) + ((k*(2*np.pi))/3)
        numerator = -(sx*np.cos(phi) + sy*np.sin(phi))
        denominator = sz - h

        s = np.arctan2(numerator, denominator)

        px = pr*np.cos(s)*np.cos(phi)
        py = pr*np.cos(s)*np.sin(phi)
        pz = pr*np.sin(s) + h

        ip.append([px, py, pz])

    return np.array(ip)

# --- PANEL FRAME ---
def get_panel(ipts, sun_pos):
    center = np.array([0, 0, h])
    p0, p1, p2 = ipts[0], ipts[1], ipts[2]
    v1 = p1 - p0
    v2 = p2 - p0

    real_normal = sun_pos - center
    real_normal /= np.linalg.norm(real_normal)

    normal = np.cross(v1, v2)
    normal /= np.linalg.norm(normal)

    u = v1 / np.linalg.norm(v1)
    v = np.cross(normal, u)
    v /= np.linalg.norm(v)

    r = np.linspace(0, pr, 15)
    t = np.linspace(0, 2*np.pi, 60)
    R, T = np.meshgrid(r, t)

    X = center[0] + R*np.cos(T)*u[0] + R*np.sin(T)*v[0]
    Y = center[1] + R*np.cos(T)*u[1] + R*np.sin(T)*v[1]
    Z = center[2] + R*np.cos(T)*u[2] + R*np.sin(T)*v[2]

    return real_normal, normal, X, Y, Z

# --- SCENE SETUP ---
fig = plt.figure(figsize=(13, 8))
ax = fig.add_subplot(111, projection='3d')

ax.set_xlim(-100, 100)
ax.set_ylim(-100, 100)
ax.set_zlim(0, 130)

# Base Disk
theta = np.linspace(0, 2*np.pi, 60)
r = np.linspace(0, br, 20)
T, R = np.meshgrid(theta, r)
ax.plot_surface(R*np.cos(T), R*np.sin(T), np.zeros_like(R), color='lightgreen', alpha=0.25)

bpts = get_bpts()

# --- OBJECTS ---
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

# --- TEXT BLOCKS ---
sun_text = ax.text2D(1.05, 0.95, "", transform=ax.transAxes, fontsize=12, va='top', color='orange')

leg_texts = []
y_positions = [0.88, 0.66, 0.44]
for k in range(3):
    t = ax.text2D(1.05, y_positions[k], "", transform=ax.transAxes, fontsize=10, va='top', color=link_colors[k])
    leg_texts.append(t)

tilt_text = ax.text2D(1.05, 0.22, "", transform=ax.transAxes, fontsize=12, va='top', color='red')

panel_surf = None

# --- UPDATE FUNCTION ---
def update(frame):
    global panel_surf

    total = 200
    ang = (frame - total/2) / (total/2)

    # SUN
    sx = -120*np.sin(ang)
    sy = -80*np.sin(ang)
    sz = 120*np.cos(ang)
    sun = np.array([sx, sy, sz])

    ipts = get_ipts(sun)

    real_normal, normal, PX, PY, PZ = get_panel(ipts, sun)

    required_deg = np.degrees(np.arccos(real_normal[2]))
    tilt_deg = np.degrees(np.arccos(normal[2]))
    max_tilt_deg = np.degrees(max_s)
    status = "TRACKING" if required_deg < max_tilt_deg else "OUT OF RANGE"

    if status == "OUT OF RANGE":
        gray = "gray"
        panel_color = "gray"
        tilt_text.set_color(gray)
        sun_text.set_color(gray)
        ipts_scatter.set_color(gray)

        # legs + leg texts gray
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

    # ---- UPDATE SCATTERS ----
    sun_scatter._offsets3d = ([sx], [sy], [sz])
    ipts_scatter._offsets3d = (ipts[:, 0], ipts[:, 1], ipts[:, 2])

    # ---- LEG LINES + TEXT ----
    for k in range(3):
        base = bpts[k]
        panel_pt = ipts[k]
        next_base = bpts[(k+1) % 3]

        # (rapordaki gibi 3 noktalı polyline: base -> panel -> next_base)
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

    # ---- REDRAW PANEL ----
    if panel_surf is not None:
        panel_surf.remove()

    panel_surf = ax.plot_surface(PX, PY, PZ, color=panel_color, alpha=1, linewidth=0.5)

    # ---- TEXT BLOCK ----
    tilt_text.set_text(
        f"Max Zenith: {max_tilt_deg:5.2f}\n"
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