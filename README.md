#  Sun-Tracking Six-Leg Panel System
## Mathematical Modeling and 3D Simulation

This project presents the **mathematical modeling, kinematic analysis, and real-time 3D simulation** of a sun-tracking solar panel system driven by a six-leg parallel mechanism inspired by the **Stewart platform** architecture.

The system continuously adjusts the orientation of the solar panel so that its normal vector aligns with the Sun’s direction, maximizing solar energy efficiency.

---

##  Overview

Solar panels generate maximum power when they directly face the Sun. Fixed or limited-axis systems cannot maintain optimal orientation throughout the day, resulting in significant energy loss.

This project develops a **six-degree-of-freedom (6-DOF) parallel mechanism model** that enables continuous and precise sun tracking using mathematical modeling and numerical simulation.

The study integrates geometric modeling, kinematic formulation, and Python-based visualization to simulate the dynamic behavior of the system.

---

##  Objectives

The main objectives of this project are:

- Develop a mathematical model for a six-leg sun-tracking mechanism  
- Determine panel orientation based on Sun position  
- Compute dynamic leg lengths required for tracking  
- Respect mechanical tilt constraints  
- Visualize system motion using real-time 3D simulation  

---

##  System Description

The system consists of:

- A fixed circular **base platform**
- A movable circular **solar panel platform**
- Six adjustable legs connecting base and panel
- A dynamic **Sun position vector**

### At each simulation step:

1. The Sun position is computed.
2. The panel normal vector is aligned with the Sun direction.
3. The tilt angle is calculated within mechanical limits.
4. Panel attachment points are updated.
5. Leg vectors and lengths are computed.
6. The system is rendered in a 3D environment.

---

##  Mathematical Modeling

The model is based on:

- vector geometry  
- coordinate frame transformations  
- trigonometric relations  
- rotation and orientation constraints  
- Euclidean distance calculations  

The panel tilt angle is determined so that the panel surface remains orthogonal to the Sun direction while respecting physical actuator limits.

---

##  Simulation Features

- Real-time 3D visualization  
- Dynamic panel orientation control  
- Continuous leg length variation  
- Animated Sun motion  
- Mechanical tilt constraint handling  
- Out-of-range detection with visual warning  
- Live system state and geometry display  

---

##  Technologies Used

- **Python 3**
- **NumPy** — numerical computation
- **Matplotlib** — 3D visualization & animation

---

##  Project Structure
```
sun-tracking-six-leg-panel-system/
│
├── sun_tracking_six_leg_panel.py   # main simulation code
├── README.md
└└── docs/
      └── six_leg_panel_system.pdf
```
## 📄 Academic Report

You can read the full academic report here:

📥 [Download PDF](docs/six_leg_panel_system.pdf)

## Author

**Aleyna Özdoğan**  