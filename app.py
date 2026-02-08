import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# Page Config
st.set_page_config(page_title="Chaos Dashboard", layout="wide")

# Sidebar
st.sidebar.title("🎛️ Controls")
app_mode = st.sidebar.selectbox("Choose Simulation", ["Home", "Random Walk", "Mandelbrot"])

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
    
    # 1. Sidebar Controls (Specific to this simulation)
    st.sidebar.markdown("---")
    st.sidebar.header("Fractal Settings")
    iterations = st.sidebar.slider("Complexity (Iterations)", 10, 200, 50)
    zoom = st.sidebar.slider("Zoom Level", 1.0, 10.0, 1.0)
    
    # 2. The Logic (Vectorized for Speed)
    def get_fractal(h, w, max_iter, zoom_factor):
        # Create a grid of complex numbers
        y, x = np.ogrid[-1.5:1.5:h*1j, -2.5:1.5:w*1j]
        c = (x + y*1j) / zoom_factor
        z = c
        divtime = max_iter + np.zeros(z.shape, dtype=int)

        # The Iteration Loop
        for i in range(max_iter):
            z = z**2 + c
            diverge = z*np.conj(z) > 2**2            # Check who escaped
            div_now = diverge & (divtime == max_iter)  # Mark first escapees
            divtime[div_now] = i                     # Record escape time
            z[diverge] = 2                           # Cap runaway values

        return divtime

    # 3. The Render
    st.write(f"Rendering with **{iterations}** iterations at **{zoom}x** zoom.")
    
    if st.button("Generate Fractal"):
        with st.spinner("Calculating..."):
            # Generate the image data
            fractal_data = get_fractal(600, 800, iterations, zoom)
            
            # Plot using Matplotlib
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(fractal_data, cmap='inferno')
            ax.axis("off") # Hide the axes for a cleaner look
            st.pyplot(fig)