import numpy as np
from scipy.integrate import solve_ivp


def _derivatives(t, state, m1, m2, l1, l2, g):
    """
    Computes the time derivatives of the state vector using the
    equations of motion derived from the Lagrangian (T - V).

    State vector: [theta1, omega1, theta2, omega2]
    where omega = d(theta)/dt (angular velocity)

    Returns: [d(theta1)/dt, d(omega1)/dt, d(theta2)/dt, d(omega2)/dt]
             = [omega1, alpha1, omega2, alpha2]
    where alpha = d(omega)/dt (angular acceleration)
    """
    theta1, omega1, theta2, omega2 = state

    # Angle difference — appears in both coupled ODE expressions
    delta = theta2 - theta1

    # --- Denominator terms (shared across both equations) ---
    # These come from solving the 2x2 matrix system that results
    # from applying Euler-Lagrange to both generalized coordinates.
    denom1 = (m1 + m2) * l1 - m2 * l1 * np.cos(delta) ** 2
    denom2 = (l2 / l1) * denom1

    # --- Angular acceleration of pendulum 1 (alpha1) ---
    # Derived from d/dt(∂L/∂ω1) - ∂L/∂θ1 = 0
    alpha1 = (
        m2 * l1 * omega1**2 * np.sin(delta) * np.cos(delta)
        + m2 * g * np.sin(theta2) * np.cos(delta)
        + m2 * l2 * omega2**2 * np.sin(delta)
        - (m1 + m2) * g * np.sin(theta1)
    ) / denom1

    # --- Angular acceleration of pendulum 2 (alpha2) ---
    # Derived from d/dt(∂L/∂ω2) - ∂L/∂θ2 = 0
    alpha2 = (
        -m2 * l2 * omega2**2 * np.sin(delta) * np.cos(delta)
        + (m1 + m2) * g * np.sin(theta1) * np.cos(delta)
        - (m1 + m2) * l1 * omega1**2 * np.sin(delta)
        - (m1 + m2) * g * np.sin(theta2)
    ) / denom2

    return [omega1, alpha1, omega2, alpha2]


def simulate(theta1_deg, theta2_deg, omega1, omega2, m1, m2, l1, l2, g, t_max, num_steps):
    """
    Integrates the equations of motion using scipy's solve_ivp (RK45).

    Parameters
    ----------
    theta1_deg, theta2_deg : float
        Initial angles in degrees (converted internally to radians).
    omega1, omega2 : float
        Initial angular velocities in rad/s.
    m1, m2 : float
        Masses in kg.
    l1, l2 : float
        Arm lengths in meters.
    g : float
        Gravitational acceleration (9.81 default).
    t_max : float
        Simulation duration in seconds.
    num_steps : int
        Number of time points to evaluate.

    Returns
    -------
    t : np.ndarray, shape (num_steps,)
        Time values.
    sol : np.ndarray, shape (num_steps, 4)
        State vectors [theta1, omega1, theta2, omega2] at each time step.
    x1, y1 : np.ndarray
        Cartesian coordinates of mass 1.
    x2, y2 : np.ndarray
        Cartesian coordinates of mass 2.
    """
    # Convert degrees to radians
    theta1_0 = np.radians(theta1_deg)
    theta2_0 = np.radians(theta2_deg)

    state0 = [theta1_0, omega1, theta2_0, omega2]
    t_span = (0, t_max)
    t_eval = np.linspace(0, t_max, num_steps)

    result = solve_ivp(
        fun=_derivatives,
        t_span=t_span,
        y0=state0,
        t_eval=t_eval,
        args=(m1, m2, l1, l2, g),
        method="RK45",
        rtol=1e-8,   # Tight tolerance — chaotic systems amplify integration error
        atol=1e-8,
    )

    t = result.t
    sol = result.y.T  # Transpose to shape (num_steps, 4)

    theta1 = sol[:, 0]
    theta2 = sol[:, 2]

    # Convert polar (theta, L) to Cartesian coordinates
    # Origin at pivot point; y increases downward (standard pendulum convention)
    x1 = l1 * np.sin(theta1)
    y1 = -l1 * np.cos(theta1)

    x2 = x1 + l2 * np.sin(theta2)
    y2 = y1 - l2 * np.cos(theta2)

    return t, sol, x1, y1, x2, y2


def calculate_energy(sol, m1, m2, l1, l2, g):
    """
    Computes total mechanical energy (T + V) at each time step.

    Drift in energy is a diagnostic for numerical error — useful for
    demonstrating integration quality in the UI
    """
    theta1 = sol[:, 0]
    omega1 = sol[:, 1]
    theta2 = sol[:, 2]
    omega2 = sol[:, 3]

    delta = theta2 - theta1

    # Kinetic energy — directly from T in the Lagrangian
    T = (
        0.5 * (m1 + m2) * l1**2 * omega1**2
        + 0.5 * m2 * l2**2 * omega2**2
        + m2 * l1 * l2 * omega1 * omega2 * np.cos(delta)
    )

    # Potential energy — V = -[(m1+m2)*g*l1*cos(theta1) + m2*g*l2*cos(theta2)]
    # (negative because y increases downward in our coordinate convention)
    V = -(m1 + m2) * g * l1 * np.cos(theta1) - m2 * g * l2 * np.cos(theta2)

    return T + V