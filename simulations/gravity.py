import numpy as np
from scipy.integrate import odeint 
from scipy.integrate import solve_ivp

# Gravitational Constant
G = 1.0 

def three_body_equations(state, t, m1, m2, m3, epsilon):
    """
    The core physics engine.
    'state' is an array of 18 numbers:
    [x1, y1, z1, x2, y2, z2, x3, y3, z3, vx1, vy1, vz1, vx2, vy2, vz2, vx3, vy3, vz3]
    """
    # 1. UNPACK POSITIONS
    r1 = state[0:3]
    r2 = state[3:6]
    r3 = state[6:9]
    
    # 2. UNPACK VELOCITIES (The first half of our derivatives!)
    v1 = state[9:12]
    v2 = state[12:15]
    v3 = state[15:18]
    
    # 3. CALCULATE DISTANCE VECTORS
    r12 = r2 - r1
    r13 = r3 - r1
    r23 = r3 - r2
    
    # Calculate magnitudes (adding a tiny number to prevent divide-by-zero crashes)
    norm_r12 = np.linalg.norm(r12) + epsilon
    norm_r13 = np.linalg.norm(r13) + epsilon
    norm_r23 = np.linalg.norm(r23) + epsilon
    
    # 4. CALCULATE ACCELERATIONS (The second half of our derivatives!)
    # F = G * m1 * m2 / r^3 * vector_r  =>  a = F / m
    a1 = G * m2 * r12 / norm_r12**3 + G * m3 * r13 / norm_r13**3
    a2 = G * m1 * (-r12) / norm_r12**3 + G * m3 * r23 / norm_r23**3
    a3 = G * m1 * (-r13) / norm_r13**3 + G * m2 * (-r23) / norm_r23**3
    
    # 5. REPACK THE DERIVATIVES [velocities, accelerations]
    derivatives = np.concatenate((v1, v2, v3, a1, a2, a3))
    
    return derivatives

def simulate_orbit(initial_state, t_max, num_steps, masses, epsilon):
    """
    Hands the equations to the Scipy solver and returns the history.
    """
    t = np.linspace(0, t_max, num_steps)
    m1, m2, m3 = masses
    
    # Scipy integrates the derivatives over time t
    solution = odeint(three_body_equations, initial_state, t, args=(m1, m2, m3, epsilon))
    
    return solution, t
def calculate_energy(solution, masses, epsilon):
    m1, m2, m3 = masses
    # solution is (Steps, 18). Extract positions and velocities
    r1, r2, r3 = solution[:, 0:3], solution[:, 3:6], solution[:, 6:9]
    v1, v2, v3 = solution[:, 9:12], solution[:, 12:15], solution[:, 15:18]

    # Kinetic Energy: Sum of 0.5 * m * v^2
    ke = 0.5 * (m1 * np.sum(v1**2, axis=1) + 
                m2 * np.sum(v2**2, axis=1) + 
                m3 * np.sum(v3**2, axis=1))

    # Potential Energy: -m1*m2 / (dist + epsilon)
    def dist(p1, p2): return np.sqrt(np.sum((p1 - p2)**2, axis=1)) + epsilon
    
    pe = -(m1*m2/dist(r1, r2) + m1*m3/dist(r1, r3) + m2*m3/dist(r2, r3))
    
    return ke + pe # Total Energy