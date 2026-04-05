import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def get_color_map(cmap_name):
    """Returns a matplotlib colormap object."""
    return plt.get_cmap(cmap_name)

def generate_mandelbrot(xmin, xmax, ymin, ymax, width, height, max_iter):
    x = np.linspace(xmin, xmax, width)
    y = np.linspace(ymin, ymax, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    
    # CRITICAL FIX: Initialize with max_iter (Light color)
    # This ensures the "Inside" of the set is visible against the background.
    div_time = np.zeros(Z.shape, dtype=int) + max_iter

    mask = np.ones(Z.shape, dtype=bool)

    for i in range(max_iter):
        Z[mask] = Z[mask]**2 + C[mask]
        diverged = np.abs(Z) > 2
        
        # Overwrite "Outside" points with low numbers (Dark color)
        div_time[mask & diverged] = i
        
        mask[diverged] = False
        if not np.any(mask):
            break
            
    return div_time