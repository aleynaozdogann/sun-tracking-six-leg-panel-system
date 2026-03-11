#  Sun-Tracking Six-Leg Panel System
## Mathematical Modeling, Simulation and Future AI Integration

This project presents the **mathematical modeling, kinematic analysis, and real-time 3D simulation** of a sun-tracking solar panel system driven by a **six-leg parallel mechanism inspired by the Stewart platform architecture**.

The system dynamically adjusts the orientation of the solar panel so that its **normal vector aligns with the Sun's direction**, maximizing solar energy exposure.

The project originated as an **academic mathematical modeling study** and is being further developed into a **simulation-driven engineering project with future machine learning integration**.

---

#  Project Overview

Solar panels generate maximum energy when their surface is perpendicular to incoming sunlight. Fixed panels or limited-axis tracking systems cannot maintain this optimal orientation throughout the day.

This project develops a **six-degree-of-freedom (6-DOF) parallel mechanism model** capable of continuously adjusting the panel orientation to track the Sun.

The work integrates:

- mathematical modeling  
- kinematic analysis  
- numerical simulation  
- real-time 3D visualization  
- robotics-inspired mechanism design  

The system simulates how a **Stewart platform based structure** could be used to control solar panel orientation in real-time.

---

#  Objectives

The main objectives of this project are:

- Develop a **mathematical model for a six-leg solar tracking mechanism**  
- Compute **solar direction vectors over time**  
- Align the **panel normal vector with the Sun**  
- Calculate **required actuator leg lengths**  
- Respect **mechanical tilt constraints**  
- Visualize system behavior through **3D simulation**  

---

# ⚙ System Description

The simulated system consists of:

- a fixed circular **base platform**  
- a movable circular **solar panel platform**  
- **six adjustable legs** connecting base and panel  
- a dynamic **Sun position vector**

### At each simulation step

1. The Sun position is calculated.  
2. The panel normal vector is aligned with the Sun direction.  
3. Tilt constraints are applied.  
4. Panel attachment points are updated.  
5. Leg vectors and lengths are calculated.  
6. The system state is rendered in a **3D environment**.

---

#  Mathematical Modeling

The mathematical model is based on:

- vector geometry  
- coordinate transformations  
- trigonometric relations  
- rotation matrices  
- orientation constraints  
- Euclidean distance calculations  

The panel orientation is determined so that the panel surface remains **orthogonal to the Sun direction**, while respecting mechanical tilt limitations.

---

#  Simulation Features

The simulation includes:

- real-time **3D visualization**  
- animated **Sun motion**  
- dynamic **panel orientation**  
- continuous **leg length adjustment**  
- mechanical **tilt constraint handling**  
- **out-of-range detection**  
- live **system state visualization**

---

#  Technologies Used

- **Python**
- **NumPy** — numerical computation
- **Matplotlib** — 3D visualization & animation

---

#  Project Structure

```
sun-tracking-six-leg-panel-system
│
├── docs/
│   └── six_leg_panel_system.pdf
│
├── src/
│   ├── main.py
│   ├── simulation.py
│   ├── kinematics.py
│   ├── solar_math.py
│   └── utils.py
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

# Future Development

This project is being extended beyond simulation toward a **data-driven solar optimization system**.

Planned improvements include:

- synthetic dataset generation from simulation  
- machine learning models for optimal panel angle prediction  
- energy optimization experiments  
- weather-aware solar tracking  
- improved visualization and system monitoring  

These extensions aim to combine **mathematical modeling, simulation engineering, and machine learning**.

---

#  Academic Report

The full academic study describing the mathematical modeling and simulation of the system is available here:

 **[Download PDF](docs/six_leg_panel_system.pdf)**

---

#  Author

**Aleyna Özdoğan**

Mathematics graduate interested in:

- Artificial Intelligence  
- Simulation Engineering  
- Computational Modeling  
- Data Science