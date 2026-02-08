import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Page Config
st.set_page_config(page_title="Chaos Dashboard", layout="wide")

# Sidebar
st.sidebar.title("🎛️ Controls")
app_mode = st.sidebar.selectbox("Choose Simulation", ["Home", "Random Walk", "Mandelbrot", "Polymer Simulator"])

if app_mode == "Home":
    st.title("The Chaos Dashboard")
    st.write("### Status: Online 🟢")
    st.write("Welcome back, Alex. The physics engine is ready.")
    st.write("Select a simulation from the sidebar to begin.")

elif app_mode == "Random Walk":
    st.title("Brownian Motion Generator")
    
    # User Inputs
    steps = st.sidebar.slider("Number of Steps", 100, 10000, 1000)
    
    if st.button("Generate Walk"):
        # The Math
        x = np.cumsum(np.random.randn(steps))
        y = np.cumsum(np.random.randn(steps))
        
        # The Plot
        fig, ax = plt.subplots()
        ax.plot(x, y, alpha=0.7, linewidth=0.8)
        ax.set_title(f"Random Walk ({steps} steps)")
        
        # The Streamlit Magic
        st.pyplot(fig)
        st.success(f"Generated walk with {steps} steps.")

elif app_mode == "Mandelbrot":
    st.title("Mandelbrot Set Explorer")
    
    # 1. Navigation Controls
    st.sidebar.markdown("---")
    st.sidebar.header("Navigation")
    center_x = st.sidebar.number_input("Center X", value=-0.5, step=0.1, format="%.5f")
    center_y = st.sidebar.number_input("Center Y", value=0.0, step=0.1, format="%.5f")
    zoom = st.sidebar.number_input("Zoom Multiplier", min_value=1.0, value=1.0, step=1.0)
    
    # 2. Render Settings
    st.sidebar.header("Render Settings")
    iterations = st.sidebar.slider("Complexity (Iterations)", 10, 1000, 100)
    res_multiplier = st.sidebar.slider("Resolution Scale", 0.5, 3.0, 1.0, step=0.5)
    
    # 3. The Logic
    def get_fractal(max_iter, zoom_factor, cx, cy, res_mult):
        # Calculate pixel grid size based on resolution slider
        w = int(800 * res_mult)
        h = int(600 * res_mult)
        
        # Calculate viewport boundaries based on zoom and center
        x_width = 4.0 / zoom_factor
        y_height = 3.0 / zoom_factor
        
        x_min, x_max = cx - x_width/2, cx + x_width/2
        y_min, y_max = cy - y_height/2, cy + y_height/2
        
        # Generate the complex grid
        y, x = np.ogrid[y_min:y_max:h*1j, x_min:x_max:w*1j]
        c = x + y*1j
        z = c
        divtime = max_iter + np.zeros(z.shape, dtype=int)

        # The Iteration Loop
        for i in range(max_iter):
            z = z**2 + c
            diverge = z*np.conj(z) > 2**2            
            div_now = diverge & (divtime == max_iter) 
            divtime[div_now] = i                     
            z[diverge] = 2                           

        return divtime

    # 4. The Render (Fixed: Dedented to run OUTSIDE the function)
    if st.button("Generate Fractal"):
        with st.spinner("Calculating..."):
            # Generate the image data
            fractal_data = get_fractal(iterations, zoom, center_x, center_y, res_multiplier)
            
            # Plot using Matplotlib
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(fractal_data, cmap='inferno')
            ax.axis("off") 
            st.pyplot(fig)

elif app_mode == "Polymer Simulator":
    st.title("Polymer Chain Physics")
    # FIXED: Added 'r' before the string to treat backslashes as raw text
    st.markdown(r"""
    **The Science:** A "Real" polymer cannot occupy the same space twice (Excluded Volume). 
    * **Good Solvent:** The chain is "stiff" and expands to maximize surface area ($R \approx N^{0.6}$).
    * **Bad Solvent:** The chain is "sticky" and clumps together locally ($R \approx N^{0.33}$).
    """)

    # 1. Configuration
    col1, col2 = st.columns(2)
    with col1:
        # Increased max N to 5000 for better stats
        N = st.slider("Number of Monomers (N)", 100, 5000, 1000) 
        step_size = st.slider("Kuhn Length (b)", 0.1, 5.0, 1.0)
    with col2:
        solvent = st.selectbox("Solvent Quality", ["Theta Solvent (Ideal)", "Good Solvent (Swollen)", "Bad Solvent (Collapsed)"])
        
    with st.expander("Realism Settings", expanded=True):
        excluded_vol = st.checkbox("Enable Excluded Volume (Self-Avoiding Walk)", value=True)
        st.caption("Note: 'Bad Solvent' needs this OFF to collapse fully. 'Good Solvent' needs this ON to swell.")

    # 2. The Physics Engine (Final "Pearl Necklace" Logic)
    def generate_polymer(N, step_size, solvent_type, use_saw):
        x = np.zeros(N)
        y = np.zeros(N)
        z = np.zeros(N)
        
        # Scaling factors
        scaling = 1.0
        if solvent_type == "Good Solvent (Swollen)":
            scaling = 1.0 
        elif solvent_type == "Bad Solvent (Collapsed)":
            scaling = 0.8 

        for i in range(1, N):
            # Try to find a valid step
            max_retries = 50 if use_saw else 1 # Increased retries to avoid "giving up"
            best_x, best_y, best_z = x[i-1], y[i-1], z[i-1]
            
            for attempt in range(max_retries):
                # 1. Generate Raw Step (Random Direction)
                theta = np.random.uniform(0, 2*np.pi)
                phi = np.random.uniform(0, np.pi)
                
                dx = step_size * np.sin(phi) * np.cos(theta) * scaling
                dy = step_size * np.sin(phi) * np.sin(theta) * scaling
                dz = step_size * np.cos(phi) * scaling
                
                # 2. Apply Solvent Physics (TO EVERY ATTEMPT)
                
                # GOOD SOLVENT: Geometric Stiffness
                if solvent_type == "Good Solvent (Swollen)" and i > 1:
                    prev_dx = x[i-1] - x[i-2]
                    prev_dy = y[i-1] - y[i-2]
                    prev_dz = z[i-1] - z[i-2]
                    
                    # Add Bias (Strength 1.0)
                    dx += prev_dx * 1.0
                    dy += prev_dy * 1.0
                    dz += prev_dz * 1.0
                    
                    # Renormalize to ensure length is exactly 'step_size'
                    current_len = np.sqrt(dx**2 + dy**2 + dz**2)
                    dx = (dx / current_len) * step_size
                    dy = (dy / current_len) * step_size
                    dz = (dz / current_len) * step_size

                # BAD SOLVENT: Local Attraction
                elif solvent_type == "Bad Solvent (Collapsed)" and i > 100:
                    start_node = max(0, i-100)
                    local_cm_x = np.mean(x[start_node:i])
                    local_cm_y = np.mean(y[start_node:i])
                    local_cm_z = np.mean(z[start_node:i])
                    
                    dx += (local_cm_x - x[i-1]) * 0.2
                    dy += (local_cm_y - y[i-1]) * 0.2
                    dz += (local_cm_z - z[i-1]) * 0.2
                    
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
                
                # Save as fallback
                best_x, best_y, best_z = cand_x, cand_y, cand_z

                # 4. Excluded Volume Check (SAW)
                if use_saw:
                    # Check ALL previous atoms
                    dists = (x[:i] - cand_x)**2 + (y[:i] - cand_y)**2 + (z[:i] - cand_z)**2
                    if np.min(dists) >= (step_size * 0.8)**2:
                        break # Valid step found!
            
            # Commit
            x[i], y[i], z[i] = best_x, best_y, best_z
            
        return x, y, z

    # 3. Computation & Metrics
    if st.button("Synthesize Polymer"):
        with st.spinner("Simulating molecular dynamics..."):
            x, y, z = generate_polymer(N, step_size, solvent, excluded_vol)
            
            # Metrics
            r_end = np.sqrt((x[-1]-x[0])**2 + (y[-1]-y[0])**2 + (z[-1]-z[0])**2)
            
            cm_x, cm_y, cm_z = np.mean(x), np.mean(y), np.mean(z)
            rg_sq = np.mean((x-cm_x)**2 + (y-cm_y)**2 + (z-cm_z)**2)
            rg = np.sqrt(rg_sq)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("End-to-End Distance", f"{r_end:.2f}")
            c2.metric("Radius of Gyration", f"{rg:.2f}")
            
            # Flory Exponent
            if r_end > 0:
                exponent = np.log(r_end / step_size) / np.log(N)
            else:
                exponent = 0.0
            c3.metric("Flory Exponent (ν)", f"{exponent:.3f}")

            # 4. Visualization (Refined)
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Main Chain: Smaller dots (s=2) for high N
            ax.scatter(x, y, z, c=np.arange(N), cmap='cool', s=2, alpha=0.6, edgecolors='none')
            
            # Thin line to show connectivity
            ax.plot(x, y, z, alpha=0.2, color='white', lw=0.5)
            
            # Markers: Slightly smaller (s=50)
            ax.scatter(x[0], y[0], z[0], color='lime', s=50, label='Start', edgecolors='white')
            ax.scatter(x[-1], y[-1], z[-1], color='red', s=50, label='End', edgecolors='white')
            
            # Center of Mass
            ax.scatter(cm_x, cm_y, cm_z, color='yellow', marker='x', s=50, label='Center of Mass')

            ax.set_facecolor('#0E1117') 
            ax.grid(False) 
            ax.axis('off') 
            ax.legend()
            st.pyplot(fig)