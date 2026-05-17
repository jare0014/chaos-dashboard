# Chaos Dashboard: Computational Physics & Dynamical Systems
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

A modular, web-based computational physics engine designed to simulate and analyze deterministic chaos, orbital mechanics, and complex fractal geometry. Built with Python and deployed via Streamlit Cloud.

## 🚀 Live Demo
**[Access the live interactive dashboard here](https://chaos-dashboard-khpbj6y6jeedqurug9j6m4.streamlit.app/)**

## ⚙️ Engine Modules & Architecture

### 1. Three-Body Orbit (Gravitational Instability)
A numerical integration of the n-body problem, highlighting phase-space divergence and sensitive dependence on initial conditions.
* **Solver Engine:** Utilizes SciPy's `DOP853` (explicit 8th-order Runge-Kutta method) for high-precision temporal stepping.
* **Numerical Diagnostics:** Features real-time tracking of truncation errors and artificial energy dissipation inherent to non-symplectic integrators. Includes automated Lyapunov divergence detection tracking systemic energy variance at a 10^-3 J threshold.

### 2. The Mandelbrot Set (Recursive Complexity)
Explores how simple quadratic iterations generate infinite, self-similar fractal structures mapping the boundary of stability in the complex plane.
* **Optimization:** Replaces standard nested iterative loops with NumPy vectorized broadcasting, reducing compute time by >90% for high-resolution renders and ensuring zero-lag client-side performance.
* **Scientific Documentation:** Features an embedded technical Markdown paper (`/fractal_explorer/README.md`) analyzing complex dynamics, bifurcation thresholds, and Julia set transitions.
* **Data Sonification:** Includes a standalone Python explorer that maps the orbital periods of bounded coordinates into audible frequency signals, translating geometric stability into audio data.
* **High-Performance Rendering:** Contains a batch-rendering script configured to compute and output ultra-high-resolution (4K) fractal phase maps.

### 3. Double Pendulum (Coupled Nonlinear Oscillations)
A classic demonstration of Hamiltonian Chaos. Simulates two linked pendulums to visualize how coupled degrees of freedom lead to complex, non-periodic motion.
* **Architecture:** Solves coupled second-order ordinary differential equations (ODEs) using high-precision matrix transformations to evaluate instantaneous angular acceleration.

### 4. Stochastic Polymer Growth (Statistical Complexity)
Demonstrates how microscopic uncertainty leads to macroscopic scaling laws in polymer chains using random walks. 

## 🛠️ Local Installation & Usage

To mirror this environment locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/jare0014/chaos-dashboard.git](https://github.com/jare0014/chaos-dashboard.git)
   cd chaos-dashboard
   ```
2. **Initialize the Virtual Environment & Install Dependencies:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```
3. Launch the Dashboard:

```Bash
streamlit run app.py
```