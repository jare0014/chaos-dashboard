import numpy as np
import matplotlib.pyplot as plt
import time

#The Core Physics Engine
def mandelbrot(h, w, max_iter=100):
    """
    Calculates the Mandelbrot set.
    h,w: Height and Width of the map in pixels.
    """
# 1. Grid Creation (Complex Plane)
# Use numpy's broadcasting to create grid of complex numbers.
# Real axis (x): -2.0 to 0.5
# Imaginary axis (y): -1.2 to 1.2
    y, x = np.ogrid[-1.2:1.2:h*1j, -2.:0.5:w*1j]
    c = x+y*1j

    # 2. Initialization
    z = c
    # divtime stores "escape times"
    divtime = max_iter + np.zeros(z.shape, dtype=int)

    # 3. The Loop (Iterate z = z^2+c)
    for i in range(max_iter):
        z = z**2 + c

        # Check which points have escaped (magnitude >2)
        diverge = z*np.conj(z) > 2**2
        div_now = diverge & (divtime == max_iter)

        divtime[div_now] = i
        z[diverge] = 2

    return divtime

# --- MAIN EXECUTION -- 
print("Computing fractal")
start = time.time()

mandel_img = mandelbrot(1000,1000)

plt.figure(figsize=(10, 10))

# VISUALIZATION
#'cmap' controls the solors. Try 'magma', 'hot', 'bone', 'jet')
plt.imshow(mandel_img.T, cmap='inferno', extent=[-2.0, 0.5, -1.2, 1.2])
plt.title(f"Mandelbrot Set (Computed in {time.time() - start:.2f}s)")
plt.xlabel("Re(c)")
plt.ylabel("Im(c)")

# Save the artifact
plt.savefig("mandelbrot.png", dpi=300)
print("Done. Saved to mandelbrot.png")
