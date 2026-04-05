## Chaos Dashboard
An Interactive Explorer for Emergent Complexity and Nonlinear Dynamics

This Streamlit-based dashboard serves as a computational sandbox for simulating complex systems. By iterating simple mathematical rules, these modules visualize the transition from order to chaos across various physical and mathematical domains.

## The Simulation Modules
### 1. The Mandelbrot Set: Recursive Complexity

Core Logic: Uses the **Escape Time Algorithm** to map the boundary of stability in the complex plane. This module explores how simple quadratic iterations generate infinite, self-similar fractal structures.

### 2. Stochastic Polymer Growth (Statistical Complexity)
Core Logic: While traditional chaos is deterministic, this module explores Statistical Chaos. It uses random walks to demonstrate how microscopic uncertainty (entropy) leads to macroscopic scaling laws in polymer chains.

### 3. Three-Body Orbit: Gravitational Instability

Core Logic: A numerical integration of the n-body problem, highlighting **Sensitive Dependence on Initial Conditions**. This module demonstrates the inherent unpredictability in deterministic gravitational systems.

### 4. Double Pendulum: Coupled Nonlinear Oscillations

Core Logic: A classic demonstration of **Hamiltonian Chaos**. By simulating two linked pendulums, this module visualizes how coupled degrees of freedom lead to complex, non-periodic motion.

## Setup & Synchronization
To mirror this environment on a secondary machine, follow these steps:

Clone the repository:
git clone https://github.com/jare0014/chaos-dashboard.git

Initialize the Virtual Environment:
python -m venv venv

Install the required dependencies:
pip install -r requirements.txt

Launch the dashboard:
./run.bat