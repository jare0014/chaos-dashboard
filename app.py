import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# --- IMPORT THE NEW ENGINES ---
# If this fails, make sure you created 'simulations/__init__.py'
from simulations import fractal
from simulations import polymer

# 1. Page Config
st.set_page_config(page_title="Stochastic Physics", layout="wide")

# 2. Sidebar Navigation
st.sidebar.title("Physics Dashboard")
app_mode = st.sidebar.selectbox("Choose Simulation", 
    ["Mandelbrot Explorer", "Polymer Simulator"])

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