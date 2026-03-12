import numpy as np

# --- PARAMETERS ---
br = 30.0
pr = 15.0
h = 40.0
max_s = np.arctan(h / br)

# --- BASE POINTS ---
def get_bpts():
    pts = []
    for k in range(3):
        angle = k * (2 * np.pi) / 3
        pts.append([br * np.cos(angle), br * np.sin(angle), 0.0])
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
        phi = (np.pi / 3) + ((k * (2 * np.pi)) / 3)
        numerator = -(sx * np.cos(phi) + sy * np.sin(phi))
        denominator = sz - h

        s = np.arctan2(numerator, denominator)

        px = pr * np.cos(s) * np.cos(phi)
        py = pr * np.cos(s) * np.sin(phi)
        pz = pr * np.sin(s) + h

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
    t = np.linspace(0, 2 * np.pi, 60)
    R, T = np.meshgrid(r, t)

    X = center[0] + R * np.cos(T) * u[0] + R * np.sin(T) * v[0]
    Y = center[1] + R * np.cos(T) * u[1] + R * np.sin(T) * v[1]
    Z = center[2] + R * np.cos(T) * u[2] + R * np.sin(T) * v[2]

    return real_normal, normal, X, Y, Z