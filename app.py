import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# --- IMPORT THE NEW ENGINES ---
# If this fails, make sure you created 'simulations/__init__.py'
from simulations import fractal
from simulations import polymer
from simulations import gravity
from simulations import pendulum 

# 1. Page Config
st.set_page_config(page_title="Stochastic Physics", layout="wide")

# 2. Sidebar Navigation
st.sidebar.title("Physics Dashboard")
app_mode = st.sidebar.selectbox("Choose Simulation", 
    ["Mandelbrot Explorer", "Polymer Simulator", "Three-Body Gravitation", "Double Pendulum"])

# --- MODE 1: FRACTALS (The Chaos Engine) ---
if app_mode == "Mandelbrot Explorer":
    st.title("The Mandelbrot Set")
    st.markdown("Explore the boundary of the complex plane.")

    # UI Controls
    col1, col2 = st.columns(2)
    with col1:
        # Increase the max to 2000 for cleaner edges
        max_iter = st.slider("Precision (Iterations)", 50, 2000, 100)
        zoom = st.slider("Zoom Level", 1.0, 1000.0, 1.0)
    with col2:
        pan_x = st.number_input("Pan X", value=-0.75, step=0.05, format="%.6f")
        pan_y = st.number_input("Pan Y", value=0.1, step=0.05, format="%.6f")
        
    # NEW SLIDER: Resolution Quality
    quality = st.select_slider("Image Quality", options=["Low (Fast)", "Medium", "High (Slow)", "Ultra (4K)"], value="Medium")
    
    # Map quality to pixels
    res_map = {"Low (Fast)": 400, "Medium": 800, "High (Slow)": 1200, "Ultra (4K)": 2000}
    w = h = res_map[quality]
        
    # Viewport Math (UI Logic only - mapping screen to complex plane)
    x_width = 3.0 / zoom
    y_height = 3.0 / zoom
    xmin, xmax = pan_x - x_width/2, pan_x + x_width/2
    ymin, ymax = pan_y - y_height/2, pan_y + y_height/2

    if st.button("Generate Fractal"):
        with st.spinner("Computing chaos..."):
            # 1. Run the Engine
            img = fractal.generate_mandelbrot(xmin, xmax, ymin, ymax, w, h, max_iter)
            
            # --- NEW DISPLAY LOGIC ---
            
            # 2. Color Mapping (Manual)
            # We map the raw iteration counts (integers) to colors (RGBA) directly.
            # This bypasses Matplotlib's "Figure" overhead.
            
            # Normalize to 0.0 - 1.0
            norm_img = img / max_iter 
            
            # Apply the colormap (returns a [Width, Height, 4] array)
            cmap = plt.get_cmap('hot')
            colored_img = cmap(norm_img)
            
            # 3. Display raw pixels
            # 'use_column_width=False' ensures it doesn't get squished.
            # You will see a scrollbar if the image is wider than the screen.
            st.image(colored_img, caption=f"Resolution: {w}x{h}", use_container_width=False)

# --- MODE 2: POLYMERS (The Stochastic Engine) ---
elif app_mode == "Polymer Simulator":
    st.title("Polymer Chain Physics")
    st.markdown(r"""
    **The Physics of Scaling Laws ($R \sim N^{\nu}$):**
    
    * **🟢 Good Solvent (Swollen):** Monomers repel each other. The chain swells to maximize entropy.
        $$R \approx N^{3/5} \approx N^{0.588}$$
    
    * **🟡 Theta Solvent (Ideal):** Repulsion exactly balances attraction. Behaves like a pure Random Walk.
        $$R \approx N^{1/2} = N^{0.500}$$
    
    * **🔴 Bad Solvent (Collapsed):** Monomers attract each other. The chain collapses into a dense globule.
        $$R \approx N^{1/3} \approx N^{0.333}$$
    """)

    # UI Controls
    col1, col2 = st.columns(2)
    with col1:
        N = st.slider("Number of Monomers (N)", 100, 5000, 1000) 
        step_size = st.slider("Kuhn Length (b)", 0.1, 5.0, 1.0)
    with col2:
        solvent = st.selectbox("Solvent Quality", [
            "Theta Solvent (Ideal)", 
            "Good Solvent (Swollen)", 
            "Bad Solvent (Collapsed)"
        ])
        
    use_saw = st.checkbox("Enable Excluded Volume (SAW)", value=True)

    if st.button("Synthesize Polymer"):
        with st.spinner("Simulating molecular dynamics..."):
            # 1. Generate Raw Data
            x, y, z = polymer.generate_polymer(N, step_size, solvent, use_saw)
            
            # 2. Physics Analysis (Standard Metrics)
            metrics = polymer.analyze_chain(x, y, z)
            
            # Unpack the dictionary for easier use
            r_end = metrics["end_to_end"]
            rg = metrics["radius_of_gyration"]
            cx, cy, cz = metrics["center_of_mass"]
            
            # 3. Scaling Analysis (The Restored Feature)
            # Calculate the specific exponent for THIS chain using the formula: nu = log(R/b) / log(N)
            measured_nu = np.log(r_end / step_size) / np.log(N)

            # ... (after calculating measured_nu) ...

            # 4. Determine Theoretical Limit based on User Selection
            if "Good" in solvent:
                theoretical_nu = 0.588  # Flory exponent for 3D SAW
                solvent_type = "Swollen"
            elif "Bad" in solvent:
                theoretical_nu = 0.333  # 1/3 for collapsed sphere
                solvent_type = "Globule"
            else:
                theoretical_nu = 0.500  # 1/2 for random walk
                solvent_type = "Ideal"

            # --- DISPLAY METRICS (Now with 4 Columns) ---
            c1, c2, c3, c4 = st.columns(4)
            
            c1.metric("End-to-End", f"{r_end:.2f}")
            c2.metric("Radius of Gyration", f"{rg:.2f}")
            
            # The Comparison
            c3.metric("Measured ν", f"{measured_nu:.3f}")
            c4.metric("Theoretical ν", f"{theoretical_nu:.3f}", help="The expected scaling for this solvent type")
            
            # --- VISUALIZATION ---
            fig = plt.figure(figsize=(10, 8))
            ax = fig.add_subplot(111, projection='3d')
            
            # Plot the chain (Rainbow color by index)
            ax.scatter(x, y, z, c=np.arange(N), cmap='cool', s=2, alpha=0.6)
            ax.plot(x, y, z, alpha=0.2, color='white', lw=0.5)
            
            # MARKERS
            # Start (Green)
            ax.scatter(x[0], y[0], z[0], color='lime', s=100, label='Start', edgecolors='black')
            # End (Red)
            ax.scatter(x[-1], y[-1], z[-1], color='red', s=100, label='End', edgecolors='black')
            # Center of Mass (Gold Star)
            ax.scatter(cx, cy, cz, color='gold', s=200, marker='*', label='Center of Mass', edgecolors='black')
            
            # STYLING (The Void)
            ax.set_facecolor('#0E1117') 
            ax.axis('off')
            ax.grid(False)
            
            # Legend
            ax.legend(facecolor='#0E1117', labelcolor='white')
            
            st.pyplot(fig)
# --- MODE 3: THE THREE-BODY PROBLEM ---
elif app_mode == "Three-Body Gravitation":
    st.title("Three-Body Orbital Mechanics")
    st.markdown("A brute-force numerical integration of Newton's Law of Universal Gravitation.")

    # --- PRESETS DICTIONARY ---
    presets = {
        "Default (Randomized Slingshot)": [
            1.0, 1.0, 1.0,  # Masses (m1, m2, m3)
            -1.0, 0.0, 0.0,  1.0, 0.0, 0.0,  0.0, 1.0, 0.0, # Positions (x,y,z) x 3
            0.0, -0.5, 0.0,  0.0, 0.5, 0.0,  0.5, 0.0, 0.0  # Velocities (vx,vy,vz) x 3
        ],
        "The Figure-8 (Stable)": [
            1.0, 1.0, 1.0, 
            0.97000436, -0.24308753, 0.0,  -0.97000436, 0.24308753, 0.0,  0.0, 0.0, 0.0,
            -0.46620368, -0.43236573, 0.0,  -0.46620368, -0.43236573, 0.0,  0.93240737, 0.86473146, 0.0
        ]
    }

    # --- SESSION STATE MANAGEMENT ---
    # We initialize a flat list of 21 keys for our grid
    keys = ["m1","m2","m3", "x1","y1","z1","x2","y2","z2","x3","y3","z3", "vx1","vy1","vz1","vx2","vy2","vz2","vx3","vy3","vz3"]
    
    # If the user hasn't loaded the page yet, give them the default numbers
    if "gravity_state" not in st.session_state:
        st.session_state.gravity_state = presets["Default (Randomized Slingshot)"]

    def load_preset():
        """Callback to overwrite the vault and force-update individual widget keys"""
        choice = st.session_state.preset_choice
        new_values = presets[choice]
        
        # 1. Update the master state (for consistency)
        st.session_state.gravity_state = new_values.copy()
        
        # 2. Extract the data chunks
        masses = new_values[0:3]
        pos = new_values[3:12]
        vel = new_values[12:21]
        
        # 3. Overwrite the specific keys for all 3 bodies
        for i in range(3):
            st.session_state[f"m_{i}"] = float(masses[i])
            
            st.session_state[f"x_{i}"] = float(pos[i*3])
            st.session_state[f"y_{i}"] = float(pos[i*3+1])
            st.session_state[f"z_{i}"] = float(pos[i*3+2])
            
            st.session_state[f"vx_{i}"] = float(vel[i*3])
            st.session_state[f"vy_{i}"] = float(vel[i*3+1])
            st.session_state[f"vz_{i}"] = float(vel[i*3+2])
    def generate_random_state():
        """Generates random coordinates and injects them into the session state vault"""
        import numpy as np
        v_mult = st.session_state.v_scale # Grab the velocity multiplier from the slider
        
        for i in range(3):
            # Masses: Strictly positive (0.5 to 2.5)
            st.session_state[f"m_{i}"] = float(np.random.uniform(0.5, 2.5))
            
            # Positions: Between -2.0 and 2.0
            st.session_state[f"x_{i}"] = float(np.random.uniform(-2.0, 2.0))
            st.session_state[f"y_{i}"] = float(np.random.uniform(-2.0, 2.0))
            st.session_state[f"z_{i}"] = float(np.random.uniform(-2.0, 2.0))
            
            # Velocities: Slower to prevent instant ejections (-0.1 to 0.1)
            st.session_state[f"vx_{i}"] = float(np.random.uniform(-0.1, 0.1)) 
            st.session_state[f"vy_{i}"] = float(np.random.uniform(-0.1, 0.1)) 
            st.session_state[f"vz_{i}"] = float(np.random.uniform(-0.1, 0.1))
    def adjust_v_plus():
        st.session_state.v_scale = round(min(2.0, st.session_state.v_scale + 0.01), 2)

    def adjust_v_minus():
        st.session_state.v_scale = round(max(0.0, st.session_state.v_scale - 0.01), 2)        
    
# --- TOP UI: PRESETS, RANDOMIZER, ENERGY & TIME ---
# max_render_points: How many dots to actually draw on the screen
    max_render_points = st.sidebar.select_slider(
        "Visual Resolution", 
        options=[500, 1000, 2500, 5000], 
        value=1000,
        help="Higher resolution shows more detail but can lag the 3D view."
)
# num_steps: Total number of data points to calculate
    num_steps = st.sidebar.slider("Calculation Steps", 500, 10000, 2000, step=500)
# steps_per_day: How many snapshots to take per 24 hours of simulation
    steps_per_day = st.sidebar.slider("Snapshots per Day", 50, 1000, 200, step=50)
#trail size: How many of those snapshots to show in the trail    
    trail_size = st.slider("Trail Length (points)", 5, num_steps, 500, key="trail_len")
    colA, colB, colC, colD, colE = st.columns([2, 1, 1, 1, 1]) # Extra column for epsilon
    with colA:
        st.selectbox("Load Initial Conditions", list(presets.keys()), key="preset_choice", on_change=load_preset)
    with colB:
        st.button("🎲 Randomize", on_click=generate_random_state, use_container_width=True)
    with colC:
        st.write("Velocity Multiplier")
        # Create a mini-grid for the buttons and slider
        v_col1, v_col2, v_col3 = st.columns([1, 3, 1])
        
        with v_col1:
            st.button("➖", on_click=adjust_v_minus, use_container_width=True)
        
        with v_col2:
            # We remove the label here since we wrote it above to save space
            st.slider("v_slider", 0.0, 2.0, key="v_scale", label_visibility="collapsed")
        
        with v_col3:
            st.button("➕", on_click=adjust_v_plus, use_container_width=True)
    with colD:
        t_max = st.slider("Simulation Time (Days)", 1, 100, 10)
    with colE: # New column for epsilon
        epsilon = st.slider(
            "Softening Factor (ε)", 
            min_value=1e-8, 
            max_value=1.0,    # Increased max so you can actually feel the "squishiness"
            value=1e-4,       # Start at a visible value
            step=1e-5,        # Explicitly set the step size
            format="%.2e",    # Use scientific notation to see the precision
            key="epsilon"
)
            
    # --- THE 7x3 COCKPIT GRID ---
    state = st.session_state.gravity_state # Grab current numbers
    
    # Create 3 columns for the 3 bodies
    cols = st.columns(3)
    bodies = ["Body 1 (Red)", "Body 2 (Blue)", "Body 3 (Green)"]
    
    # We loop to build the 21 inputs cleanly without writing 21 lines of code!
    new_state = []
    idx = 0
    
    # Extract data for looping
    masses = state[0:3]
    pos = state[3:12]
    vel = state[12:21]

    for i in range(3):
        with cols[i]:
            st.markdown(f"**{bodies[i]}**")
            m = st.number_input("Mass", key=f"m_{i}", format="%.8f")
            
            st.caption("Position (x, y, z)")
            x = st.number_input("X", key=f"x_{i}", format="%.8f")
            y = st.number_input("Y", key=f"y_{i}", format="%.8f")
            z = st.number_input("Z", key=f"z_{i}", format="%.8f")
            
            st.caption("Velocity (vx, vy, vz)")
            vx = st.number_input("Vx", key=f"vx_{i}", format="%.8f")
            vy = st.number_input("Vy", key=f"vy_{i}", format="%.8f")
            vz = st.number_input("Vz", key=f"vz_{i}", format="%.8f")
            
            # Store the user's current inputs back into a list
            new_state.append((m, x, y, z, vx, vy, vz))

# Grab the live slider value
    current_v_scale = st.session_state.v_scale
# Extract masses
    user_masses = [new_state[0][0], new_state[1][0], new_state[2][0]]
    # Re-pack with the velocity throttle applied!
    user_initial_state = [
        new_state[0][1], new_state[0][2], new_state[0][3],  # Pos 1
        new_state[1][1], new_state[1][2], new_state[1][3],  # Pos 2
        new_state[2][1], new_state[2][2], new_state[2][3],  # Pos 3
        new_state[0][4] * current_v_scale, new_state[0][5] * current_v_scale, new_state[0][6] * current_v_scale,  # Vel 1
        new_state[1][4] * current_v_scale, new_state[1][5] * current_v_scale, new_state[1][6] * current_v_scale,  # Vel 2
        new_state[2][4] * current_v_scale, new_state[2][5] * current_v_scale, new_state[2][6] * current_v_scale   # Vel 3
    ]

# --- EXECUTE ENGINE ---
    if st.button("Calculate Orbits", type="primary", use_container_width=True):
        with st.spinner("Crunching the numbers..."):
            
            # 1. Define resolution
            num_steps_sim = int(t_max * steps_per_day)
            
            # 2. RUN SIMULATION
            # Note: Ensure gravity.simulate_orbit returns (solution, time_steps)
            solution, time_steps = gravity.simulate_orbit(
                user_initial_state, t_max, num_steps_sim, user_masses, epsilon
            )
            
            total_energy = gravity.calculate_energy(solution, user_masses, epsilon)

            # --- OPTIMIZED VISUALIZATION ---
            import plotly.graph_objects as go
            
            points_per_day = num_steps_sim / t_max
            actual_trail_size = int(trail_size * points_per_day)
            start_idx = max(0, num_steps_sim - actual_trail_size)

            # Define render_step ONCE here so it's available for both charts
            render_step = max(1, actual_trail_size // max_render_points)

            fig = go.Figure()
            colors = ['red', 'cyan', 'lime']
            
            for i in range(3):
                idx = i * 3
                x = solution[start_idx::render_step, idx]
                y = solution[start_idx::render_step, idx + 1]
                z = solution[start_idx::render_step, idx + 2]
                
                fig.add_trace(go.Scatter3d(
                    x=x, y=y, z=z,
                    mode='lines',
                    line=dict(width=3, color=colors[i]),
                    name=f'Body {i+1}'
                ))
                
                fig.add_trace(go.Scatter3d(
                    x=[solution[-1, idx]], y=[solution[-1, idx+1]], z=[solution[-1, idx+2]],
                    mode='markers',
                    marker=dict(size=6, color=colors[i]),
                    showlegend=False
                ))

            fig.update_layout(
                template="plotly_dark",
                margin=dict(l=0, r=0, b=0, t=0),
                scene=dict(aspectmode='cube'),
                hovermode=False
            )

            st.plotly_chart(fig, use_container_width=True)

            # --- TIME-INDEXED ENERGY CHART ---
            st.divider()
            st.subheader("🚀 System Stability (Total Energy)")
            
            energy_data = {
                "Time (Days)": time_steps[::render_step],
                "Total Energy": total_energy[::render_step]
            }
            st.line_chart(energy_data, x="Time (Days)", y="Total Energy")

            # --- SIMULATION LOG & COLLISION DETECTOR ---
            # Now acting as the final "Diagnostic Footer"
            st.divider()
            st.subheader("📡 Simulation Log")
            
            pos1 = solution[:, 0:3]
            pos2 = solution[:, 3:6]
            pos3 = solution[:, 6:9]

            dist12 = np.linalg.norm(pos1 - pos2, axis=1)
            dist13 = np.linalg.norm(pos1 - pos3, axis=1)
            dist23 = np.linalg.norm(pos2 - pos3, axis=1)

            min12, min13, min23 = np.min(dist12), np.min(dist13), np.min(dist23)
            overall_min = min(min12, min13, min23)

            if overall_min == min12:
                min_idx = np.argmin(dist12)
                pair = "Body 1 (Red) & Body 2 (Cyan)"
            elif overall_min == min13:
                min_idx = np.argmin(dist13)
                pair = "Body 1 (Red) & Body 3 (Lime)"
            else:
                min_idx = np.argmin(dist23)
                pair = "Body 2 (Cyan) & Body 3 (Lime)"

            min_time = time_steps[min_idx]

            st.info(f"**Closest Encounter:** {pair} came within `{overall_min:.6e}` units of each other on **Day {min_time:.2f}**.")
            
            if overall_min < epsilon:
                st.error(f"⚠️ **Numerical Collision!** Bodies passed closer than the Softening Factor (ε = {epsilon}). The energy calculations at Day {min_time:.2f} are likely unstable.")
            else:
                st.success("✅ Minimum distance remained larger than the Softening Factor. Physics are bounded.")

# --- MODE 4: DOUBLE PENDULUM ---
elif app_mode == "Double Pendulum":
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    st.title("Double Pendulum: Hamiltonian Chaos")
    st.markdown(
        "Two linked pendulums governed by coupled nonlinear ODEs derived from the **Lagrangian (T − V)**. "
        "A classic demonstration of **sensitive dependence on initial conditions** — "
        "infinitesimal differences in starting angle produce wildly divergent trajectories."
    )

    # --- SESSION STATE INIT ---
    if "dp_result" not in st.session_state:
        st.session_state.dp_result = None

    # --- SIDEBAR CONTROLS ---
    st.sidebar.subheader("Simulation Settings")
    t_max = st.sidebar.slider("Simulation Time (s)", 5, 60, 20)
    num_steps = st.sidebar.slider("Integration Steps", 1000, 20000, 5000, step=500)
    trail_frac = st.sidebar.slider("Trail Length (%)", 10, 100, 40)

    # --- PARAMETER GRID ---
    st.subheader("Initial Conditions")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Pendulum 1**")
        m1 = st.slider("Mass 1 (kg)", 0.1, 5.0, 1.0, step=0.1)
        l1 = st.slider("Length 1 (m)", 0.1, 3.0, 1.0, step=0.1)
        theta1_deg = st.slider("Initial Angle θ₁ (°)", -180, 180, 120)
        omega1 = st.slider("Initial Angular Velocity ω₁ (rad/s)", -5.0, 5.0, 0.0, step=0.1)

    with col2:
        st.markdown("**Pendulum 2**")
        m2 = st.slider("Mass 2 (kg)", 0.1, 5.0, 1.0, step=0.1)
        l2 = st.slider("Length 2 (m)", 0.1, 3.0, 1.0, step=0.1)
        theta2_deg = st.slider("Initial Angle θ₂ (°)", -180, 180, 120)
        omega2 = st.slider("Initial Angular Velocity ω₂ (rad/s)", -5.0, 5.0, 0.0, step=0.1)

    g = 9.81  # Fixed — not a tunable parameter

    # --- CHAOS DEMO TOGGLE ---
    st.subheader("Chaos Demonstration")
    show_chaos = st.checkbox(
        "Show chaos twin (θ₁ + 0.01°)",
        value=False,
        help="Runs a second simulation with θ₁ offset by 0.01°. "
             "Watch identical-looking starts produce completely different trajectories."
    )

    # --- RUN BUTTON ---
    if st.button("Run Simulation", type="primary", use_container_width=True):
        with st.spinner("Integrating equations of motion..."):
            # Primary simulation
            t, sol, x1, y1, x2, y2 = pendulum.simulate(
                theta1_deg, theta2_deg, omega1, omega2,
                m1, m2, l1, l2, g, t_max, num_steps
            )
            energy = pendulum.calculate_energy(sol, m1, m2, l1, l2, g)

            result = {
                "t": t, "sol": sol,
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2,
                "energy": energy,
                "twin": None
            }

            # Chaos twin simulation (theta1 + 0.01 degrees)
            if show_chaos:
                t2, sol2, x1b, y1b, x2b, y2b = pendulum.simulate(
                    theta1_deg + 0.01, theta2_deg, omega1, omega2,
                    m1, m2, l1, l2, g, t_max, num_steps
                )
                result["twin"] = {"x1": x1b, "y1": y1b, "x2": x2b, "y2": y2b, "sol": sol2}

            st.session_state.dp_result = result

 # ================================================================
# REPLACE EVERYTHING FROM:
#   "# --- DISPLAY RESULTS ---"
# TO THE END OF THE ELIF BLOCK WITH THIS
# ================================================================

    # --- DISPLAY RESULTS ---
    if st.session_state.dp_result is not None:
        r      = st.session_state.dp_result
        t      = r["t"]
        sol    = r["sol"]
        x1, y1 = r["x1"], r["y1"]
        x2, y2 = r["x2"], r["y2"]
        energy = r["energy"]

        # Trail window (shared across all tabs)
        trail_len   = max(10, int(len(t) * trail_frac / 100))
        start       = max(0, len(t) - trail_len)
        render_step = max(1, trail_len // 3000)

        xs1 = x1[start::render_step]
        ys1 = y1[start::render_step]
        xs2 = x2[start::render_step]
        ys2 = y2[start::render_step]

        total_reach = l1 + l2

        # ── TABS ──────────────────────────────────────────────────────
        tab_anim, tab_trail, tab_energy = st.tabs(
            ["🎬 Animation", "📊 Trail & Phase Space", "⚡ Energy"]
        )

        # ══════════════════════════════════════════════════════════════
        # TAB 1 — ANIMATION
        # ══════════════════════════════════════════════════════════════
        with tab_anim:
            st.caption(
                "Tip: hit ▶ Play. Use the slider to scrub. "
                "Trail shows the last 15% of each frame's history."
            )

            MAX_FRAMES  = 300
            frame_step  = max(1, len(t) // MAX_FRAMES)
            frame_idx   = np.arange(0, len(t), frame_step)
            num_frames  = len(frame_idx)
            anim_trail  = max(5, num_frames // 7)  # ~15% of total frames

            # Build pivot → m1 → m2 arm geometry per frame
            def arm_trace(fi):
                i = frame_idx[fi]
                return go.Scatter(
                    x=[0, x1[i], x2[i]],
                    y=[0, y1[i], y2[i]],
                    mode="lines+markers",
                    line=dict(color="white", width=2),
                    marker=dict(
                        size=[5, 12, 12],
                        color=["white", "cyan", "red"]
                    ),
                    name="Arms",
                    showlegend=False
                )

            def trail_trace(fi, xi, yi, color, name):
                t_start = max(0, frame_idx[max(0, fi - anim_trail)])
                t_end   = frame_idx[fi] + 1
                return go.Scatter(
                    x=xi[t_start:t_end],
                    y=yi[t_start:t_end],
                    mode="lines",
                    line=dict(color=color, width=1.5),
                    opacity=0.6,
                    name=name,
                    showlegend=False
                )

            # Initial frame data
            init_data = [
                trail_trace(0, x2, y2, "red",  "M2 trail"),
                trail_trace(0, x1, y1, "cyan", "M1 trail"),
                arm_trace(0),
            ]

            # Chaos twin traces (if present)
            twin = r.get("twin")
            if twin:
                init_data.append(go.Scatter(
                    x=twin["x2"][0:1], y=twin["y2"][0:1],
                    mode="lines",
                    line=dict(color="orange", width=1, dash="dot"),
                    name="Twin M2",
                    showlegend=False
                ))

            # Build frames
            frames = []
            for fi in range(num_frames):
                frame_traces = [
                    trail_trace(fi, x2, y2, "red",  "M2 trail"),
                    trail_trace(fi, x1, y1, "cyan", "M1 trail"),
                    arm_trace(fi),
                ]
                if twin:
                    t_start = max(0, frame_idx[max(0, fi - anim_trail)])
                    t_end   = frame_idx[fi] + 1
                    frame_traces.append(go.Scatter(
                        x=twin["x2"][t_start:t_end],
                        y=twin["y2"][t_start:t_end],
                        mode="lines",
                        line=dict(color="orange", width=1, dash="dot"),
                        showlegend=False
                    ))

                frames.append(go.Frame(
                    data=frame_traces,
                    name=str(fi),
                    layout=go.Layout(
                        title_text=f"t = {t[frame_idx[fi]]:.2f}s"
                    )
                ))

            # Play / Pause buttons
            updatemenus = [dict(
                type="buttons",
                showactive=False,
                y=1.05, x=0.0, xanchor="left",
                buttons=[
                    dict(label="▶ Play",  method="animate",
                         args=[None, dict(frame=dict(duration=33, redraw=True),
                                          fromcurrent=True, mode="immediate")]),
                    dict(label="⏸ Pause", method="animate",
                         args=[[None], dict(frame=dict(duration=0, redraw=False),
                                            mode="immediate")])
                ]
            )]

            # Time scrub slider
            sliders = [dict(
                steps=[dict(method="animate", args=[[str(fi)],
                            dict(mode="immediate", frame=dict(duration=0, redraw=True))],
                            label=f"{t[frame_idx[fi]]:.1f}s")
                       for fi in range(0, num_frames, max(1, num_frames // 20))],
                x=0.0, y=0,
                len=1.0,
                currentvalue=dict(prefix="Time: ", visible=True, xanchor="center"),
                transition=dict(duration=0)
            )]

            fig_anim = go.Figure(
                data=init_data,
                frames=frames,
                layout=go.Layout(
                    template="plotly_dark",
                    height=540,
                    margin=dict(l=0, r=0, b=60, t=40),
                    xaxis=dict(range=[-(total_reach + 0.2), total_reach + 0.2],
                               scaleanchor="y", scaleratio=1,
                               showgrid=False, zeroline=False),
                    yaxis=dict(range=[-(total_reach + 0.2), total_reach + 0.2],
                               showgrid=False, zeroline=False),
                    updatemenus=updatemenus,
                    sliders=sliders,
                    hovermode=False
                )
            )

            st.plotly_chart(fig_anim, use_container_width=True)

        # ══════════════════════════════════════════════════════════════
        # TAB 2 — TRAIL & PHASE SPACE
        # ══════════════════════════════════════════════════════════════
        with tab_trail:
            phase_mode = st.radio(
                "Phase Space View",
                ["Unwrapped (θ₁ vs θ₂)", "Wrapped [-180°, 180°]", "Poincaré (ω₁ vs θ₁)"],
                horizontal=True
            )

            col_trail, col_phase = st.columns([0.55, 0.45])

            # ── Cartesian Trail (left) ──
            with col_trail:
                fig_trail = go.Figure()

                fig_trail.add_trace(go.Scatter(
                    x=xs1, y=ys1, mode="lines",
                    line=dict(color="cyan", width=1),
                    name="Mass 1", opacity=0.5
                ))
                fig_trail.add_trace(go.Scatter(
                    x=xs2, y=ys2, mode="lines",
                    line=dict(color="red", width=1.5),
                    name="Mass 2"
                ))
                # Current arm position
                fig_trail.add_trace(go.Scatter(
                    x=[0, x1[-1], x2[-1]],
                    y=[0, y1[-1], y2[-1]],
                    mode="lines+markers",
                    line=dict(color="white", width=2),
                    marker=dict(size=[5, 10, 10], color=["white", "cyan", "red"]),
                    showlegend=False
                ))
                # Chaos twin
                if twin:
                    fig_trail.add_trace(go.Scatter(
                        x=twin["x2"][start::render_step],
                        y=twin["y2"][start::render_step],
                        mode="lines",
                        line=dict(color="orange", width=1, dash="dot"),
                        name="Twin M2 (θ₁+0.01°)", opacity=0.7
                    ))

                fig_trail.update_layout(
                    template="plotly_dark", height=460,
                    title="Cartesian Trail",
                    margin=dict(l=0, r=0, b=0, t=40),
                    xaxis=dict(range=[-(total_reach+0.2), total_reach+0.2],
                               scaleanchor="y", scaleratio=1),
                    yaxis=dict(range=[-(total_reach+0.2), total_reach+0.2]),
                    hovermode=False
                )
                st.plotly_chart(fig_trail, use_container_width=True)

            # ── Phase Space (right) ──
            with col_phase:
                fig_phase = go.Figure()

                if phase_mode == "Unwrapped (θ₁ vs θ₂)":
                    px = np.degrees(sol[start::render_step, 0])
                    py = np.degrees(sol[start::render_step, 2])
                    xlabel, ylabel = "θ₁ (degrees, unwrapped)", "θ₂ (degrees, unwrapped)"
                    title = "Phase Space — Unwrapped"

                elif phase_mode == "Wrapped [-180°, 180°]":
                    px = (np.degrees(sol[start::render_step, 0]) + 180) % 360 - 180
                    py = (np.degrees(sol[start::render_step, 2]) + 180) % 360 - 180
                    xlabel, ylabel = "θ₁ (degrees)", "θ₂ (degrees)"
                    title = "Phase Space — Wrapped (Toroidal)"

                else:  # Poincaré
                    px = (np.degrees(sol[start::render_step, 0]) + 180) % 360 - 180
                    py = np.degrees(sol[start::render_step, 1])  # ω₁ in rad/s
                    xlabel, ylabel = "θ₁ (degrees)", "ω₁ (rad/s)"
                    title = "Poincaré Portrait — ω₁ vs θ₁"

                fig_phase.add_trace(go.Scatter(
                    x=px, y=py, mode="lines",
                    line=dict(color="violet", width=0.8),
                    opacity=0.85, name=title
                ))

                if twin and phase_mode == "Poincaré (ω₁ vs θ₁)":
                    px_tw = (np.degrees(twin["sol"][start::render_step, 0]) + 180) % 360 - 180
                    py_tw = np.degrees(twin["sol"][start::render_step, 1])
                    fig_phase.add_trace(go.Scatter(
                        x=px_tw, y=py_tw, mode="lines",
                        line=dict(color="orange", width=0.8, dash="dot"),
                        opacity=0.7, name="Twin"
                    ))

                fig_phase.update_layout(
                    template="plotly_dark", height=460,
                    title=title,
                    margin=dict(l=0, r=0, b=0, t=40),
                    xaxis_title=xlabel,
                    yaxis_title=ylabel,
                    hovermode=False
                )
                st.plotly_chart(fig_phase, use_container_width=True)

        # ══════════════════════════════════════════════════════════════
        # TAB 3 — ENERGY
        # ══════════════════════════════════════════════════════════════
        with tab_energy:
            energy_drift = float(np.max(energy) - np.min(energy))
            energy_pct   = abs(energy_drift / energy[0]) * 100 if energy[0] != 0 else 0.0

            ec1, ec2, ec3 = st.columns(3)
            ec1.metric("Initial Energy (J)", f"{energy[0]:.4f}")
            ec2.metric("Energy Drift (J)",   f"{energy_drift:.2e}")
            ec3.metric("Drift (%)",          f"{energy_pct:.4f}%")

            if energy_pct < 0.01:
                st.success("✅ Energy well-conserved. Integration is numerically stable.")
            elif energy_pct < 0.1:
                st.warning("⚠️ Mild energy drift. Consider increasing integration steps.")
            else:
                st.error("❌ Significant energy drift. Increase steps or reduce simulation time.")

            energy_render = max(1, len(t) // 3000)
            st.line_chart(
                {"Time (s)": t[::energy_render], "Total Energy (J)": energy[::energy_render]},
                x="Time (s)", y="Total Energy (J)"
            )