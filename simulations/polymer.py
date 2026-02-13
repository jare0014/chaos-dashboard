import numpy as np

def generate_polymer(N, step_size, solvent_type, use_saw):
    """
    Generates a 3D Random Walk simulating a polymer chain.
    
    Args:
        N (int): Number of monomers (steps).
        step_size (float): The Kuhn Length (bond length).
        solvent_type (str): "Good", "Bad", or "Theta" (determines physics).
        use_saw (bool): If True, prevents chain crossing (Self-Avoiding Walk).
        
    Returns:
        x, y, z (np.arrays): Coordinates of the chain.
    """
    # Physics Constants
    STIFFNESS  = 1.0   # Good Solvent: Strength of forward bias
    ATTRACTION = 0.2   # Bad Solvent: Strength of pull towards core
    LOOKBACK   = 100   # Bad Solvent: How many steps back to check for the core
    
    # Initialize arrays
    x = np.zeros(N)
    y = np.zeros(N)
    z = np.zeros(N)
    
    # Solvent Scaling (Global contraction for bad solvents)
    scaling = 1.0
    if solvent_type == "Good Solvent (Swollen)":
        scaling = 1.0 
    elif solvent_type == "Bad Solvent (Collapsed)":
        scaling = 0.8 

    for i in range(1, N):
        # Attempt to find a valid step (SAW logic)
        max_retries = 50 if use_saw else 1
        best_x, best_y, best_z = x[i-1], y[i-1], z[i-1]
        
        for attempt in range(max_retries):
            # 1. Base Step (Random Direction)
            theta = np.random.uniform(0, 2*np.pi)
            phi = np.random.uniform(0, np.pi)
            
            dx = step_size * np.sin(phi) * np.cos(theta) * scaling
            dy = step_size * np.sin(phi) * np.sin(theta) * scaling
            dz = step_size * np.cos(phi) * scaling
            
            # 2. Apply Solvent Physics
            if solvent_type == "Good Solvent (Swollen)" and i > 1:
                # Geometric stiffness (persist direction)
                prev_dx = x[i-1] - x[i-2]
                prev_dy = y[i-1] - y[i-2]
                prev_dz = z[i-1] - z[i-2]
                
                dx += prev_dx * STIFFNESS
                dy += prev_dy * STIFFNESS
                dz += prev_dz * STIFFNESS
                
                # Renormalize to maintain bond length 'b'
                current_len = np.sqrt(dx**2 + dy**2 + dz**2)
                dx = (dx / current_len) * step_size
                dy = (dy / current_len) * step_size
                dz = (dz / current_len) * step_size

            elif solvent_type == "Bad Solvent (Collapsed)" and i > LOOKBACK:
                # Local attraction (clumping)
                start_node = max(0, i - LOOKBACK)
                local_cm_x = np.mean(x[start_node:i])
                local_cm_y = np.mean(y[start_node:i])
                local_cm_z = np.mean(z[start_node:i])
                
                dx += (local_cm_x - x[i-1]) * ATTRACTION
                dy += (local_cm_y - y[i-1]) * ATTRACTION
                dz += (local_cm_z - z[i-1]) * ATTRACTION
                
                # Renormalize
                current_len = np.sqrt(dx**2 + dy**2 + dz**2)
                if current_len > 0:
                    dx = (dx / current_len) * step_size * scaling
                    dy = (dy / current_len) * step_size * scaling
                    dz = (dz / current_len) * step_size * scaling

            # 3. Candidate Position
            cand_x = x[i-1] + dx
            cand_y = y[i-1] + dy
            cand_z = z[i-1] + dz
            best_x, best_y, best_z = cand_x, cand_y, cand_z

            # 4. SAW Check (Excluded Volume)
            if use_saw:
                # Check ALL previous atoms
                dists = (x[:i] - cand_x)**2 + (y[:i] - cand_y)**2 + (z[:i] - cand_z)**2
                if np.min(dists) >= (step_size * 0.8)**2:
                    break # Success!
        
        x[i], y[i], z[i] = best_x, best_y, best_z
        
    return x, y, z
# Add this to the bottom of simulations/polymer.py

def analyze_chain(x, y, z):
    """
    Calculates physical properties of the polymer chain.
    Returns a dictionary of metrics.
    """
    # 1. Center of Mass (Vector)
    cx, cy, cz = np.mean(x), np.mean(y), np.mean(z)
    
    # 2. End-to-End Distance (Scalar)
    r_end = np.sqrt((x[-1]-x[0])**2 + (y[-1]-y[0])**2 + (z[-1]-z[0])**2)
    
    # 3. Radius of Gyration (Scalar)
    # Average squared distance from the Center of Mass
    rg_sq = np.mean((x - cx)**2 + (y - cy)**2 + (z - cz)**2)
    rg = np.sqrt(rg_sq)
    
    return {
        "center_of_mass": (cx, cy, cz),
        "end_to_end": r_end,
        "radius_of_gyration": rg
    }
def calculate_scaling_exponent(r_end, N, b):
    """
    Estimates the Flory exponent (nu) for a single chain.
    Formula: nu = log(R / b) / log(N)
    """
    if r_end <= 0 or b <= 0 or N <= 1:
        return 0.0
        
    # We use R_end for the distance scaling
    nu = np.log(r_end / b) / np.log(N)
    return nu